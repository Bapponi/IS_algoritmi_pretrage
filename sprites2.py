from abc import abstractmethod

import pygame
import os
import config
import numpy as np


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col


class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass

    def __str__(self) -> str:
        pass


class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'

    def __str__(self) -> str:
        return "Stone [" + str(self.cost()) + "] (" + str(self.row) + "," + str(self.col) + ")"


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'

    def __str__(self) -> str:
        return "Water [" + str(self.cost()) + "] (" + str(self.row) + "," + str(self.col) + ")"


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'

    def __str__(self) -> str:
        return "Road [" + str(self.cost()) + "] (" + str(self.row) + "," + str(self.col) + ")"


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'

    def __str__(self) -> str:
        return "Grass [" + str(self.cost()) + "] (" + str(self.row) + "," + str(self.col) + ")"


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'

    def __str__(self) -> str:
        return "Mud [" + str(self.cost()) + "] (" + str(self.row) + "," + str(self.col) + ")"


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'

    def __str__(self) -> str:
        return "Dune [" + str(self.cost()) + "] (" + str(self.row) + "," + str(self.col) + ")"


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    @abstractmethod
    def __get_path_to_root(self, start_row: int, start_col: int,
                           current_father_son_relations: list, index_of_father: int) -> list:
        """
        Return the list of fields from the lief: (start_row, start_col) to the tree root.

        :return: List of fields including the start field and the root field.
        :param start_row: start field row
        :param start_col: start field column
        :param current_father_son_relations: list of extended fields (row, col, father_index). father_index is the index
            of the (row, col) father
        :param index_of_father: index of (start_row, start_col) father
        """
        pass

    @abstractmethod
    def __add_neighbours_to_father_son_relations(self, neighbours: list, father_son_relations: list,
                                                 index_for_sons: int):
        """
        Add current field neighbours to the tree. Father's index for the structure (row, col, father_index),
            father_index will be index_for_sons.
        :param neighbours: List of current field neighbours
        :param father_son_relations: list that represents tree
        :param index_for_sons: current field index in father_son_relations list
        """
        pass

    @abstractmethod
    def __insert_neighbours_in_appropriate_order(self, neighbours: list, list_for_expanding: list, father_index: int):
        """
        Insert field's neighbours to the list_for_expanding in the right order. That list is the crucial for any
            algorithm, and this rule for inserting is defined by the algorithm itself.
        :param neighbours: current field's neighbours (only in 4 directions: up, right, down, left).
        :param list_for_expanding: current list of non-expanded fields. It contains fields that will be going to expand
            in the order defined by the appropriate algorithm.
        :param father_index: index of current field's father in the father_son_relations list
        """
        pass

    @abstractmethod
    def get_agent_path(self, game_map: list, goal: Goal) -> list:
        """
        Return the list of fields from start to goal field, using the Agent's specified algorithm.

        :return: Final list of fields
        :param game_map: map which is used by Agent
        :param goal: field that Agent need to reach
        """
        pass


class ExampleAgent(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def __get_path_to_root(self, start_row: int, start_col: int,
                           current_father_son_relations: list, index_of_father: int) -> list:
        pass

    def __add_neighbours_to_father_son_relations(self, neighbours: list, father_son_relations: list,
                                                 index_for_sons: int):
        pass

    def __insert_neighbours_in_appropriate_order(self, neighbours: list, list_for_expanding: list, father_index: int):
        pass

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        row = self.row
        col = self.col
        while True:
            if row != goal[0]:
                row = row + 1 if row < goal[0] else row - 1
            elif col != goal[1]:
                col = col + 1 if col < goal[1] else col - 1
            else:
                break
            path.append(game_map[row][col])
        return path


class Aki(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def __get_path_to_root(self, start_row, start_col, current_father_son_relations, index_of_father) -> list:

        path_to_root = [(start_row, start_col)]

        index = index_of_father
        while index != -1:

            father_row, father_col, next_father_index = current_father_son_relations[index]

            path_to_root.append((father_row, father_col))

            index = next_father_index

        return path_to_root

    def __get_valid_neighbours(self, game_map, current_row, current_col, current_father_son_relations,
                               index_of_father) -> list:

        # edges of the board
        top_edge = 0
        right_edge = len(game_map[current_row]) - 1
        bottom_edge = len(game_map) - 1
        left_edge = 0

        path_to_root = self.__get_path_to_root(current_row, current_col, current_father_son_relations, index_of_father)

        valid_neighbours = []

        if top_edge < current_row:
            # north direction
            next_row = current_row - 1
            next_col = current_col
            next_cost = game_map[next_row][next_col].cost()

            if (next_row, next_col) not in path_to_root:
                valid_neighbours.append((next_row, next_col, next_cost, 4))

        if current_col < right_edge:
            # east direction
            next_row = current_row
            next_col = current_col + 1
            next_cost = game_map[next_row][next_col].cost()

            if (next_row, next_col) not in path_to_root:
                valid_neighbours.append((next_row, next_col, next_cost, 3))

        if current_row < bottom_edge:
            # south direction
            next_row = current_row + 1
            next_col = current_col
            next_cost = game_map[next_row][next_col].cost()

            if (next_row, next_col) not in path_to_root:
                valid_neighbours.append((next_row, next_col, next_cost, 2))

        if left_edge < current_col:
            # west direction
            next_row = current_row
            next_col = current_col - 1
            next_cost = game_map[next_row][next_col].cost()

            if (next_row, next_col) not in path_to_root:
                valid_neighbours.append((next_row, next_col, next_cost, 1))

        return valid_neighbours

    def __add_neighbours_to_father_son_relations(self, neighbours, father_son_relations, index_for_sons):

        for neighbour in neighbours:
            father_son_relations.append((neighbour[0], neighbour[1], index_for_sons))

    def __insert_neighbours_in_appropriate_order(self, neighbours, list_for_expanding, father_index):

        neighbours.sort(key=lambda elem: (elem[2], -elem[3]))

        neighbours.reverse()

        for neighbour in neighbours:
            list_for_expanding.append((neighbour[0], neighbour[1], father_index))

    def get_agent_path(self, game_map, goal):

        row = self.row
        col = self.col

        list_for_expanding = [(row, col, -1)]
        father_son_relations = [(row, col, -1)]

        while True:

            # node expanding
            row, col, index_of_father = list_for_expanding.pop()
            index_for_sons = father_son_relations.index((row, col, index_of_father))

            neighbours = self.__get_valid_neighbours(game_map, row, col, father_son_relations, index_of_father)

            self.__add_neighbours_to_father_son_relations(neighbours, father_son_relations, index_for_sons)

            self.__insert_neighbours_in_appropriate_order(neighbours, list_for_expanding, index_for_sons)

            if (row, col) == goal:
                final_row = row
                final_col = col
                final_index_of_father = index_of_father
                break

        path_tuples = self.__get_path_to_root(final_row, final_col, father_son_relations, final_index_of_father)
        path_tuples.reverse()

        path_fields = []

        for row_col in path_tuples:
            path_fields.append(game_map[row_col[0]][row_col[1]])

        return path_fields


class Jocke(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def __get_path_to_root(self, start_row, start_col, current_father_son_relations, index_of_father) -> list:

        path_to_root = [(start_row, start_col)]

        index = index_of_father
        while index != -1:

            father_row, father_col, next_father_index = current_father_son_relations[index]

            path_to_root.append((father_row, father_col))

            index = next_father_index

        return path_to_root

    def __get_all_neighbours_except_fathers(self, game_map, current_row, current_col, father_row, father_col) -> list:
        # edges of the board
        top_edge = 0
        right_edge = len(game_map[current_row]) - 1
        bottom_edge = len(game_map) - 1
        left_edge = 0

        all_neighbours = []

        if top_edge < current_row:
            # north direction
            next_row = current_row - 1
            next_col = current_col

            if (next_row, next_col) != (father_row, father_col):
                all_neighbours.append((next_row, next_col))

        if current_col < right_edge:
            # east direction
            next_row = current_row
            next_col = current_col + 1

            if (next_row, next_col) != (father_row, father_col):
                all_neighbours.append((next_row, next_col))

        if current_row < bottom_edge:
            # south direction
            next_row = current_row + 1
            next_col = current_col

            if (next_row, next_col) != (father_row, father_col):
                all_neighbours.append((next_row, next_col))

        if left_edge < current_col:
            # west direction
            next_row = current_row
            next_col = current_col - 1

            if (next_row, next_col) != (father_row, father_col):
                all_neighbours.append((next_row, next_col))

        return all_neighbours

    def __add_neighbours_to_father_son_relations(self, neighbours, father_son_relations, index_for_sons):

        for neighbour in neighbours:
            father_son_relations.append((neighbour[0], neighbour[1], index_for_sons))

    def __get_valid_neighbours(self, game_map, current_row, current_col, current_father_son_relations, index_of_father,
                               expanded_nodes) -> list:

        # edges of the board
        top_edge = 0
        right_edge = len(game_map[current_row]) - 1
        bottom_edge = len(game_map) - 1
        left_edge = 0

        path_to_root = self.__get_path_to_root(current_row, current_col, current_father_son_relations, index_of_father)

        valid_neighbours = []

        if top_edge < current_row:
            # north direction
            next_row = current_row - 1
            next_col = current_col
            next_average = 0

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, next_average, 4])

        if current_col < right_edge:
            # east direction
            next_row = current_row
            next_col = current_col + 1
            next_average = 0

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, next_average, 3])

        if current_row < bottom_edge:
            # south direction
            next_row = current_row + 1
            next_col = current_col
            next_average = 0

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, next_average, 2])

        if left_edge < current_col:
            # west direction
            next_row = current_row
            next_col = current_col - 1
            next_average = 0

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, next_average, 1])

        return valid_neighbours

    def __calculate_average_cost_of_neighbours(self, game_map, father_row, father_col, neighbours):

        for i in range(len(neighbours)):

            current_field_row = neighbours[i][0]
            current_field_col = neighbours[i][1]

            all_neighbours_except_fathers = self.__get_all_neighbours_except_fathers(
                game_map, current_field_row, current_field_col, father_row, father_col)

            neighbours[i][2] = 0
            for current_field_neighbour in all_neighbours_except_fathers:
                neighbours[i][2] += game_map[current_field_neighbour[0]][current_field_neighbour[1]].cost()

            neighbours[i][2] /= 1.0 * len(all_neighbours_except_fathers)

    def __insert_neighbours_in_appropriate_order(self, neighbours, list_for_expanding, father_index):

        neighbours.sort(key=lambda elem: [elem[2], -elem[3]])

        for neighbour in neighbours:
            list_for_expanding.append((neighbour[0], neighbour[1], father_index))

    def __remove_more_expensive_fields(self, row, col, list_for_expanding):

        new_list_for_expanding = [field for field in list_for_expanding if field[0] != row or field[1] != col]
        return new_list_for_expanding

    def get_agent_path(self, game_map, goal):

        row = self.row
        col = self.col

        list_for_expanding = [(row, col, -1)]
        father_son_relations = [(row, col, -1)]
        expanded_nodes = []

        final_row = -1
        final_col = -1
        final_index_of_father = -1

        while True:

            row, col, index_of_father = list_for_expanding.pop(0)
            index_for_sons = father_son_relations.index((row, col, index_of_father))
            expanded_nodes.append((row, col))
            print(row, col)

            # remove potentially same nodes with bigger cost
            list_for_expanding = self.__remove_more_expensive_fields(row, col, list_for_expanding)

            neighbours = self.__get_valid_neighbours(game_map, row, col, father_son_relations, index_of_father,
                                                     expanded_nodes)

            self.__add_neighbours_to_father_son_relations(neighbours, father_son_relations, index_for_sons)

            self.__calculate_average_cost_of_neighbours(game_map, row, col, neighbours)

            self.__insert_neighbours_in_appropriate_order(neighbours, list_for_expanding, index_for_sons)

            for neighbour in neighbours:
                if (neighbour[0], neighbour[1]) == goal:

                    final_row = neighbour[0]  # this is goal position - row
                    final_col = neighbour[1]  # this is goal position - col
                    final_index_of_father = index_for_sons  # here we stop our bfs on first find of goal
                    # so we need to start from the position of goal, and to fetch its father
                    # because we are in the father's context, index_for_sons is the father's index in the goal's context
                    break

            if (final_row, final_col) != (-1, -1):
                break

        path_tuples = self.__get_path_to_root(final_row, final_col, father_son_relations, final_index_of_father)
        path_tuples.reverse()

        path_fields = []

        for row_col in path_tuples:
            path_fields.append(game_map[row_col[0]][row_col[1]])

        return path_fields


class Draza(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def __get_path_to_root(self, start_row, start_col, current_father_son_relations, index_of_father) -> list:

        path_to_root = [(start_row, start_col)]

        index = index_of_father
        while index != -1:

            father_row, father_col, next_father_index = current_father_son_relations[index]

            path_to_root.append((father_row, father_col))

            index = next_father_index

        return path_to_root

    def __get_valid_neighbours(self, game_map, current_row, current_col, current_cost, current_father_son_relations,
                               index_of_father, expanded_nodes) -> list:

        # edges of the board
        top_edge = 0
        right_edge = len(game_map[current_row]) - 1
        bottom_edge = len(game_map) - 1
        left_edge = 0

        path_to_root = self.__get_path_to_root(current_row, current_col, current_father_son_relations, index_of_father)
        number_of_fields_to_root = len(path_to_root)

        valid_neighbours = []

        if top_edge < current_row:
            # north direction
            next_row = current_row - 1
            next_col = current_col
            next_cost = game_map[next_row][next_col].cost()

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, current_cost + next_cost, number_of_fields_to_root, 4])

        if current_col < right_edge:
            # east direction
            next_row = current_row
            next_col = current_col + 1
            next_cost = game_map[next_row][next_col].cost()

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, current_cost + next_cost, number_of_fields_to_root, 3])

        if current_row < bottom_edge:
            # south direction
            next_row = current_row + 1
            next_col = current_col
            next_cost = game_map[next_row][next_col].cost()

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, current_cost + next_cost, number_of_fields_to_root, 2])

        if left_edge < current_col:
            # west direction
            next_row = current_row
            next_col = current_col - 1
            next_cost = game_map[next_row][next_col].cost()

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, current_cost + next_cost, number_of_fields_to_root, 1])

        return valid_neighbours

    def __add_neighbours_to_father_son_relations(self, neighbours, father_son_relations, index_for_sons):

        for neighbour in neighbours:
            father_son_relations.append((neighbour[0], neighbour[1], index_for_sons))

    def __insert_neighbours_in_appropriate_order(self, neighbours, list_for_expanding, father_index):

        for neighbour in neighbours:
            list_for_expanding.append((neighbour[0], neighbour[1], neighbour[2], neighbour[3], neighbour[4],
                                       father_index))

        list_for_expanding.sort(key=lambda elem: (elem[2], elem[3], -elem[4]))

    def __remove_more_expensive_fields(self, row, col, list_for_expanding):

        new_list_for_expanding = [field for field in list_for_expanding if field[0] != row or field[1] != col]
        return new_list_for_expanding

    def get_agent_path(self, game_map, goal):

        row = self.row
        col = self.col

        list_for_expanding = [(row, col, 0, 0, 0, -1)]
        father_son_relations = [(row, col, -1)]
        expanded_nodes = []

        while True:

            # node expanding
            row, col, cost, depth, direction, index_of_father = list_for_expanding.pop(0)
            index_for_sons = father_son_relations.index((row, col, index_of_father))
            expanded_nodes.append((row, col))

            # remove potentially same nodes with bigger cost
            list_for_expanding = self.__remove_more_expensive_fields(row, col, list_for_expanding)

            neighbours = self.__get_valid_neighbours(game_map, row, col, cost, father_son_relations, index_of_father,
                                                     expanded_nodes)

            self.__add_neighbours_to_father_son_relations(neighbours, father_son_relations, index_for_sons)

            self.__insert_neighbours_in_appropriate_order(neighbours, list_for_expanding, index_for_sons)

            if (row, col) == goal:
                final_row = row
                final_col = col
                final_index_of_father = index_of_father
                break

        path_tuples = self.__get_path_to_root(final_row, final_col, father_son_relations, final_index_of_father)
        path_tuples.reverse()

        path_fields = []

        for row_col in path_tuples:
            path_fields.append(game_map[row_col[0]][row_col[1]])

        return path_fields


class Bole(Agent):

    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def __get_path_to_root(self, start_row, start_col, current_father_son_relations, index_of_father) -> list:

        path_to_root = [(start_row, start_col)]

        index = index_of_father
        while index != -1:

            father_row, father_col, next_father_index = current_father_son_relations[index]

            path_to_root.append((father_row, father_col))

            index = next_father_index

        return path_to_root

    def __calculate_manhattan_distance_to_goal(self, current_row, current_col, goal_row, goal_col):
        return np.abs(current_row - goal_row) + np.abs(current_col - goal_col)

    def __calculate_manhattan_cost_to_goal(self, current_row, current_col, goal_row, goal_col):
        road_cost = 2
        return self.__calculate_manhattan_distance_to_goal(current_row, current_col, goal_row, goal_col) * road_cost

    def __get_valid_neighbours(self, game_map, current_row, current_col, current_cost, current_father_son_relations,
                               index_of_father, expanded_nodes, goal_row, goal_col) -> list:

        # edges of the board
        top_edge = 0
        right_edge = len(game_map[current_row]) - 1
        bottom_edge = len(game_map) - 1
        left_edge = 0

        path_to_root = self.__get_path_to_root(current_row, current_col, current_father_son_relations, index_of_father)
        number_of_fields_to_root = len(path_to_root)

        valid_neighbours = []

        if top_edge < current_row:
            # north direction
            next_row = current_row - 1
            next_col = current_col
            next_cost = game_map[next_row][next_col].cost()
            next_heuristic = self.__calculate_manhattan_cost_to_goal(next_row, next_col, goal_row, goal_col)

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, current_cost + next_cost + next_heuristic,
                                         number_of_fields_to_root, 4])

        if current_col < right_edge:
            # east direction
            next_row = current_row
            next_col = current_col + 1
            next_cost = game_map[next_row][next_col].cost()
            next_heuristic = self.__calculate_manhattan_cost_to_goal(next_row, next_col, goal_row, goal_col)

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, current_cost + next_cost + next_heuristic,
                                         number_of_fields_to_root, 3])

        if current_row < bottom_edge:
            # south direction
            next_row = current_row + 1
            next_col = current_col
            next_cost = game_map[next_row][next_col].cost()
            next_heuristic = self.__calculate_manhattan_cost_to_goal(next_row, next_col, goal_row, goal_col)

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, current_cost + next_cost + next_heuristic,
                                         number_of_fields_to_root, 2])

        if left_edge < current_col:
            # west direction
            next_row = current_row
            next_col = current_col - 1
            next_cost = game_map[next_row][next_col].cost()
            next_heuristic = self.__calculate_manhattan_cost_to_goal(next_row, next_col, goal_row, goal_col)

            if (next_row, next_col) not in path_to_root and (next_row, next_col) not in expanded_nodes:
                valid_neighbours.append([next_row, next_col, current_cost + next_cost + next_heuristic,
                                         number_of_fields_to_root, 1])

        return valid_neighbours

    def __add_neighbours_to_father_son_relations(self, neighbours, father_son_relations, index_for_sons):

        for neighbour in neighbours:
            father_son_relations.append((neighbour[0], neighbour[1], index_for_sons))

    def __insert_neighbours_in_appropriate_order(self, neighbours, list_for_expanding, father_index):

        for neighbour in neighbours:
            list_for_expanding.append((neighbour[0], neighbour[1], neighbour[2], neighbour[3], neighbour[4],
                                       father_index))

        list_for_expanding.sort(key=lambda elem: (elem[2], elem[3], -elem[4]))

    def __remove_more_expensive_fields(self, row, col, list_for_expanding):

        new_list_for_expanding = [field for field in list_for_expanding if field[0] != row or field[1] != col]
        return new_list_for_expanding

    def get_agent_path(self, game_map, goal):
        row = self.row
        col = self.col
        goal_row, goal_col = goal

        initial_field_cost = self.__calculate_manhattan_cost_to_goal(row, col, goal_row, goal_col)
        initial_field_depth = 0
        initial_field_direction = 0
        initial_field_father_index = -1

        list_for_expanding = [(row, col, initial_field_cost, initial_field_depth, initial_field_direction,
                               initial_field_father_index)]
        father_son_relations = [(row, col, -1)]
        expanded_nodes = []

        while True:

            # node expanding
            row, col, cost, depth, direction, index_of_father = list_for_expanding.pop(0)
            index_for_sons = father_son_relations.index((row, col, index_of_father))
            expanded_nodes.append((row, col))

            cost -= self.__calculate_manhattan_cost_to_goal(row, col, goal_row, goal_col)

            # remove potentially same nodes with bigger cost
            list_for_expanding = self.__remove_more_expensive_fields(row, col, list_for_expanding)

            neighbours = self.__get_valid_neighbours(game_map, row, col, cost, father_son_relations, index_of_father,
                                                     expanded_nodes, goal_row, goal_col)

            self.__add_neighbours_to_father_son_relations(neighbours, father_son_relations, index_for_sons)

            self.__insert_neighbours_in_appropriate_order(neighbours, list_for_expanding, index_for_sons)

            if (row, col) == goal:
                final_row = row
                final_col = col
                final_index_of_father = index_of_father
                break

        path_tuples = self.__get_path_to_root(final_row, final_col, father_son_relations, final_index_of_father)
        path_tuples.reverse()

        path_fields = []

        for row_col in path_tuples:
            path_fields.append(game_map[row_col[0]][row_col[1]])

        return path_fields


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    costMin = 100000
    path = [0, 1, 2, 3, 4, 0]

    def permutation(a, size, coin_distance):
        if size == 1:
            print("Trenutni niz", a)
            cost = 0

            for x in range(len(a) - 1):
                cost += coin_distance[a[x]][a[x+1]]

            cost += coin_distance[0][a[0]]
            cost += coin_distance[a[len(a) - 1]][0]
            print("Cena na kraju:", cost, "Globalno Min:", Jocke.costMin)

            if(cost < Jocke.costMin):
                Jocke.costMin = cost
                Jocke.path = a
                print("Trenutni najkraci put:", Jocke.path, "Najmanja cena:", Jocke.costMin)

            return
    
        print("pROSO")
        for i in range(size):
            Jocke.permutation(a, size-1, coin_distance)
    
            print("Permutacija size:", size)
            
            if size & 1:
                a[0], a[size-1] = a[size-1], a[0]
            else:
                a[i], a[size-1] = a[size-1], a[i]

            print("Kraj bloka permutacije")

    
    def get_agent_path(self, coin_distance):
        a = []
        n = len(coin_distance)

        for i in range(1, len(coin_distance)):
            a.append(i)
        
        print(a, n)

        Jocke.permutation(a, n, coin_distance)
        print("Izasao")

        return [0, 1, 2, 3, 4, 0]

class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    costMin = 100000
    path = [0, 1, 2, 3, 4, 0]

    def permutation(a, size, coin_distance):
        if size == 1:
            print("Trenutni niz", a)
            cost = 0

            for x in range(len(a) - 1):
                cost += coin_distance[a[x]][a[x+1]]

            cost += coin_distance[0][a[0]]
            cost += coin_distance[a[len(a) - 1]][0]
            print("Cena na kraju:", cost, "Globalno Min:", Micko.costMin)

            if(cost < Micko.costMin):
                Jocke.costMin = cost
                Micko.path = a
                print("Trenutni najkraci put:", Micko.path, "Najmanja cena:", Micko.costMin)

            return
    
        print("pROSO")
        for i in range(size):
            Micko.permutation(a, size-1, coin_distance)
    
            print("Permutacija size:", size)
            
            if size & 1:
                a[0], a[size-1] = a[size-1], a[0]
            else:
                a[i], a[size-1] = a[size-1], a[i]

            print("Kraj bloka permutacije")

    
    def get_agent_path(self, coin_distance):
        a = []
        n = len(coin_distance) - 1

        for i in range(1, len(coin_distance)):
            a.append(i)
        
        print(a, n)

        Micko.permutation(a, n, coin_distance)
        print("Izasao")

        return [0] + Micko.path + [0]