
import random


def binary_search(data, target, low, high):
    if low > high:
        return False

    mid = (low+high)//2 #encuentro indice de la mitad

    if target == data[mid]:
        return True
    elif target < data[mid]:
        return binary_search(data, target, low, mid-1)
    else:
        return binary_search(data, target, mid+1, high)


if __name__ == '__main__':
    data = [random.randint(0,100) for i in range(10)] #creo array de 10 numeros entre 0 y 100

    #sorted_data = sorted(data) #no modifica el array original
    data.sort()
    print(data)

    target = int(input('What number would you like to find?'))
    found = binary_search(data, target, 0, len(data)-1) #recibe datos, el elemento a buscar, el indice inicial y el final

    print(found)
