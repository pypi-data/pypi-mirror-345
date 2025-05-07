import numpy as np

def int_to_binary_list(num):
  ascii_val = ord(str(num))
  binary_val = bin(ascii_val)[2:]
  padded_binary = binary_val.zfill(8)
  return [int(digit) for digit in padded_binary]

two_d_list = []
for i in range(10):
    two_d_list.append(int_to_binary_list(i)[2:])


input = np.array(two_d_list)
input


w = np.array([0,0,0,0,0,0])
b = np.array([0])
lr = 0.1
w , b

y = np.array([0,1,0,1,0,1,0,1,0,1])
y



for i in range(len(input)):
  y_pred = np.dot(w,input[i]) + b
  if y_pred >= 0 :
    y_pred = 1
    if y[i] != y_pred:
      w = w + lr*(y[i] - y_pred)*input[i]
      b = b + lr*(y[i] - y_pred)
  else:
    y_pred < 0
    if y[i] != y_pred:
      w = w + lr*(y[i] - y_pred)*input[i]
      b = b + lr*(y[i] - y_pred)

w , b




y_predicted = []
for i in range(len(input)):
  y_pred = (np.dot(w,input[i]) + b)
  if y_pred >= 0 :
    y_pred = 1
  else:
    y_pred < 0
    y_pred = 0
  y_predicted.append(y_pred)
y_predicted