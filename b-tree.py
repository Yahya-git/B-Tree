class Node:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []


class BTree:
    def __init__(self, t):
        self.root = Node(True)
        self.t = t

    def split_node(self, node, i):
        t = self.t
        y = node.children[i]
        z = Node(y.leaf)
        node.children.insert(i + 1, z)
        node.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t : (2 * t) - 1]
        y.keys = y.keys[0 : t - 1]
        if not y.leaf:
            z.children = y.children[t : 2 * t]
            y.children = y.children[0 : t - 1]

    def insert(self, key):
        t = self.t
        root = self.root

        if len(root.keys) == (2 * t) - 1:
            new_root = Node()
            self.root = new_root
            new_root.children.insert(0, root)
            self.split_node(new_root, 0)
            self.insert_non_full(new_root, key)
        else:
            self.insert_non_full(root, key)

    def insert_non_full(self, node, key):
        t = self.t
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * t) - 1:
                self.split_node(node, i)
                if key > node.keys[i]:
                    i += 1
            self.insert_non_full(node.children[i], key)

    def delete(self, node, key):
        t = self.t
        i = 0 #Child index
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if node.leaf:
            if i < len(node.keys) and node.keys[i] == key:
                node.keys.pop(i)
            return
        if i < len(node.keys) and node.keys[i] == key:
            return self.delete_internal_node(node, key, i)
        elif len(node.children[i].keys) >= t:
            self.delete(node.children[i], key)
        else:
            if i != 0 and i + 2 < len(node.children):
                if len(node.children[i - 1].keys) >= t:
                    self.delete_sibling(node, i, i - 1)
                elif len(node.children[i + 1].keys) >= t:
                    self.delete_sibling(node, i, i + 1)
                else:
                    self.delete_merge(node, i, i + 1)
            elif i == 0:
                if len(node.children[i + 1].keys) >= t:
                    self.delete_sibling(node, i, i + 1)
                else:
                    self.delete_merge(node, i, i + 1)
            elif i + 1 == len(node.children):
                if len(node.children[i - 1].keys) >= t:
                    self.delete_sibling(node, i, i - 1)
                else:
                    self.delete_merge(node, i, i - 1)
            self.delete(node.children[i], key)

    def delete_internal_node(self, node, key, i):
        t = self.t
        if node.leaf:
            if node.keys[i] == key:
                node.keys.pop(i)
            return

        if len(node.children[i].keys) >= t:
            node.keys[i] = self.delete_predecessor(node.children[i])
            return
        elif len(node.children[i + 1].keys) >= t:
            node.keys[i] = self.delete_successor(node.children[i + 1])
            return
        else:
            self.delete_merge(node, i, i + 1)
            self.delete_internal_node(node.children[i], key, self.t - 1)

    def delete_predecessor(self, node):
        if node.leaf:
            return node.keys.pop()
        n = len(node.keys) - 1
        if len(node.children[n].keys) >= self.t:
            self.delete_sibling(node, n + 1, n)
        else:
            self.delete.merge(node, n, n + 1)
        self.delete_predecessor(node.children[n])

    def delete_successor(self, node):
        if node.leaf:
            return node.keys.pop(0)
        if len(node.children[1].keys) >= self.t:
            self.delete_sibling(node, 0, 1)
        else:
            self.delete_merge(node, 0, 1)
        self.delete_successor(node.children[0])

    def delete_merge(self, node, i, j):
        center_node = node.children[i]

        if j > i:
            right_node = node.children[j]
            center_node.keys.append(node.keys[i])
            for k in range(len(right_node.keys)):
                center_node.keys.append(right_node.keys[k])
                if len(right_node.children) > 0:
                    center_node.children.append(right_node.children[k])
            if len(right_node.children) > 0:
                center_node.children.append(right_node.children.pop())
            new = center_node
            node.keys.pop(i)
            node.children.pop(j)
        else:
            left_node = node.children[j]
            left_node.keys.append(node.keys[j])
            for i in range(len(center_node.keys)):
                left_node.keys.append(center_node.keys[i])
                if len(left_node.children) > 0:
                    left_node.children.append(center_node.children[i])
            if len(left_node.children) > 0:
                left_node.children.append(center_node.children.pop())
            new = left_node
            node.keys.pop(j)
            node.children.pop(i)

        if node == self.root and len(node.keys) == 0:
            self.root = new

    def delete_sibling(self, node, i, j):
        center_node = node.children[i]
        if i < j:
            right_node = node.children[j]
            center_node.keys.append(node.keys[i])
            node.keys[i] = right_node.keys[0]
            if len(right_node.children) > 0:
                center_node.children.append(right_node.children[0])
                right_node.children.pop(0)
            right_node.keys.pop(0)
        else:
            left_node = node.children[j]
            center_node.keys.insert(0, node.keys[i - 1])
            node.keys[i - 1] = left_node.keys.pop()
            if len(left_node.children) > 0:
                center_node.children.insert(0, left_node.children.pop())

    def search(self, key, node=None):
        node = self.root if node == None else node

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)
        elif node.leaf:
            return None
        else:
            return self.search(key, node.children[i])

    def display(self, node, level=0):
        print(f"Level {level}", end=": ")

        for i in node.keys:
            print(i, end=" ")
        print()
        level += 1

        if len(node.children) > 0:
            for i in node.children:
                self.display(i, level)


B = BTree(3)


def insert_and_search():
    # B = BTree(3)

    for i in range(10):
        B.insert(i)

    B.display(B.root)
    print()

    keys_to_search = [2, 9, 11, 4]
    for key in keys_to_search:
        if B.search(key) is not None:
            print(f"{key} is in the tree")
        else:
            print(f"{key} is NOT in the tree")


# def delete_example():
#     first_leaf = Node(True)
#     first_leaf.keys = [1, 9]

#     second_leaf = Node(True)
#     second_leaf.keys = [17, 19, 21]

#     third_leaf = Node(True)
#     third_leaf.keys = [23, 25, 27]

#     fourth_leaf = Node(True)
#     fourth_leaf.keys = [31, 32, 39]

#     fifth_leaf = Node(True)
#     fifth_leaf.keys = [41, 47, 50]

#     sixth_leaf = Node(True)
#     sixth_leaf.keys = [56, 60]

#     seventh_leaf = Node(True)
#     seventh_leaf.keys = [72, 90]

#     root_left_child = Node()
#     root_left_child.keys = [15, 22, 30]
#     root_left_child.children.append(first_leaf)
#     root_left_child.children.append(second_leaf)
#     root_left_child.children.append(third_leaf)
#     root_left_child.children.append(fourth_leaf)

#     root_right_child = Node()
#     root_right_child.keys = [55, 63]
#     root_right_child.children.append(fifth_leaf)
#     root_right_child.children.append(sixth_leaf)
#     root_right_child.children.append(seventh_leaf)

#     root = Node()
#     root.keys = [40]
#     root.children.append(root_left_child)
#     root.children.append(root_right_child)

#     B = BTree(3)
#     B.root = root
#     print('\n--- Original B-Tree ---\n')
#     B.display(B.root)

#     print('\n--- Case 1: DELETED 21 ---\n')
#     B.delete(B.root, 21)
#     B.display(B.root)

#     print('\n--- Case 2a: DELETED 30 ---\n')
#     B.delete(B.root, 30)
#     B.display(B.root)

#     print('\n--- Case 2b: DELETED 27 ---\n')
#     B.delete(B.root, 27)
#     B.display(B.root)

#     print('\n--- Case 2c: DELETED 22 ---\n')
#     B.delete(B.root, 22)
#     B.display(B.root)

#     print('\n--- Case 3b: DELETED 17 ---\n')
#     B.delete(B.root, 17)
#     B.display(B.root)

#     print('\n--- Case 3a: DELETED 9 ---\n')
#     B.delete(B.root, 9)
#     B.display(B.root)

#     print('\n--- Case X: DELETED 15 ---\n')
#     B.delete(B.root, 15)
#     B.display(B.root)


# def main():
#     print("\n--- INSERT & SEARCH ---\n")
#     # insert_and_search()
#     delete_example()


# main()
