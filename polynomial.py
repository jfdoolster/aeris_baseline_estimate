import numpy as np

def polynomaial_regression(x_arr: np.ndarray, y_arr: np.ndarray, power=1, force_zero=False, y_offset=0.0) -> (np.ndarray, np.ndarray):

    x_arr.shape = (len(x_arr),)
    y_arr.shape = (len(y_arr),1)

    x_lists = [np.ones((len(x_arr),))]
    if force_zero:
        x_lists = []

    for i in range(1,power+1):
        x_lists.append(x_arr**i)

    x_mat = np.vstack(x_lists)
    x_mat = np.transpose(x_mat)

    x_mat_prime = np.transpose(x_mat)
    x_cross_xprime = np.matmul(x_mat_prime, x_mat)
    xx_determinant = np.linalg.det(x_cross_xprime)

    if xx_determinant == 0.0:
        print("Singluar Matrix!")
        return np.empty((power+1,))

    xx_inv = np.linalg.inv(x_cross_xprime)
    xx_cross_xp = np.matmul(xx_inv, x_mat_prime)

    beta = np.matmul(xx_cross_xp, y_arr - y_offset)
    beta.shape = (len(beta), 1)

    yhat = np.matmul(x_mat, beta) + y_offset

    if force_zero:
        beta = np.insert(beta, 0, 0, axis=0)

    return beta, yhat