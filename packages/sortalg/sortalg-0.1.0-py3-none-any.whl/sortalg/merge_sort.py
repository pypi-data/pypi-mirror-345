from typing import List


def merge_sort(lst: List[int]) -> List[int]:
    def merge(A, B):
        C = []
        i = j = 0
        while i < len(A) and j < len(B):
            if A[i] < B[j]:
                C.append(A[i])
                i += 1
            else:
                C.append(B[j])
                j += 1
        for k in range(i, len(A)):
            C.append(A[k])
        for k in range(j, len(B)):
            C.append(B[k])
        return C

    def sort(A):
        if len(A) <= 1:
            return A
        B = sort(A[: len(A) // 2])
        C = sort(A[len(A) // 2 :])
        return merge(B, C)

    return sort(lst)


if __name__ == "__main__":
    import random

    A = list(range(10000))
    B = [random.choice(A) for _ in range(300)]
    C = sorted(B)
    # print(B)
    print(merge_sort(B))
    print(merge_sort(B) == C)
