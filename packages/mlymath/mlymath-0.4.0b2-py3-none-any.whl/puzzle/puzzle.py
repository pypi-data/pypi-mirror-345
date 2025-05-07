import heapq

def solve_24_num_puzzle(board_5):
    """
    整合所有功能的函数，用于求解5x5数字华容道问题。
    :param board_5: 初始5x5矩阵，格式为二维元组，例如 ((1, 2, 3, 4, 5), (6, 7, 8, 9, 10), ...)
    :return: 解决方案路径或"无解"
    """
    # 初始化方向和变量
    dx = [1, -1, 0, 0]
    dy = [0, 0, 1, -1]
    directions = ['U', 'D', 'L', 'R']  # 修改为英文标准字母表示
    hs = 0

    def get_heuristic_best(state, target, n):
        nonlocal hs
        hs += 1
        heuristic = 0
        for i, char in enumerate(state):
            if char != '0':
                target_idx = target.index(char)
                current_row, current_col = divmod(i, n)
                target_row, target_col = divmod(target_idx, n)
                heuristic += abs(current_row - target_row) + abs(current_col - target_col)
        return heuristic

    def swap(s, i, j):
        chars = list(s)
        chars[i], chars[j] = chars[j], chars[i]
        return ''.join(chars)

    def board_to_string(board, n):
        def to_base_25(num):
            if num == 0:
                return '0'
            base_25 = ''
            while num > 0:
                remainder = num % 25
                base_25 = (chr(48 + remainder) if remainder < 10 else chr(65 + remainder - 10)) + base_25
                num //= 25
            return base_25
        return ''.join(to_base_25(num) if num != 0 else '0' for row in board for num in row)
    
    if board_5 is not None:
        n = 5
        target = "123456789ABCDEFGHIJKLMNO0"
        start = board_to_string(board_5, n)
        beam_width = 2000

        heap = [(get_heuristic_best(start, target, n), 0, start, '', [])]
        visited = set()
        heapq.heapify(heap)

        while heap:
            next_level = []
            for _ in range(min(len(heap), beam_width)):
                _, steps, current, path, manhattan_distances = heapq.heappop(heap)

                if current == target:
                    return f"{path}"

                if current in visited:
                    continue

                visited.add(current)

                zero_pos = current.index('0')
                x, y = divmod(zero_pos, n)

                for i in range(4):
                    new_x, new_y = x + dx[i], y + dy[i]
                    new_pos = new_x * n + new_y
                    if 0 <= new_x < n and 0 <= new_y < n:
                        new_state = swap(current, zero_pos, new_pos)
                        if new_state not in visited:
                            new_manhattan_distance = get_heuristic_best(new_state, target, n)
                            new_manhattan_distances = manhattan_distances + [new_manhattan_distance]
                            new_cost = new_manhattan_distance + steps + 1
                            heapq.heappush(next_level, (
                                new_cost, steps + 1, new_state, path + directions[i], new_manhattan_distances))

            heap = next_level
            heapq.heapify(heap)

        return ""

def puzzle_help():
    print("以下是可用的函数：")
    print("- solve_24_num_puzzle(board_5):\n    solve_24_num_puzzle 函数用于求解 5x5 数字华容道问题。\n    参数：\n      board_5: 初始 5x5 矩阵，格式为二维元组，例如 ((1, 2, 3, 4, 5), (6, 7, 8, 9, 10), ...)。\n    返回值：\n      如果有解，则返回解决方案路径（字符串形式），例如 'UURDL'。\n      如果无解，则返回空字符串。")
    print("- puzzle_help:\n    puzzle_help 函数用于打印可用函数的帮助信息。")