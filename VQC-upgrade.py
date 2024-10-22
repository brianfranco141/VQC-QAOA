from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

THRESHOLD = 0.5

def load_data(contract_id):
  data = api.option_chain(contract_id).chain
  prices = []
  large_position_detected = []
  dark_pool_order_detected = []
  momentum = []
  for contract in data:
    prices.append(contract.last_price)
    large_position_detected.append(contract.large_position_detected)
    dark_pool_order_detected.append(contract.dark_pool_order_detected)
    momentum.append(contract.momentum)
  return {"prices": prices, "large_position_detected": large_position_detected, "dark_pool_order_detected": dark_pool_order_detected, "momentum": momentum}

def train_model(data):
  n = len(data["prices"])
  training_set = {"prices": data["prices"][:n//2], "large_position_detected": data["large_position_detected"][:n//2], "dark_pool_order_detected": data["dark_pool_order_detected"][:n//2], "momentum": data["momentum"][:n//2]}
  testing_set = {"prices": data["prices"][n//2:], "large_position_detected": data["large_position_detected"][n//2:], "dark_pool_order_detected": data["dark_pool_order_detected"][n//2:], "momentum": data["momentum"][n//2:]}
  q = QuantumRegister(3)
  c = ClassicalRegister(3)
  qc = QuantumCircuit(q, c)
    qc.u3(theta[0], theta[1], theta[2], q[0])
  qc.cx(q[0], q[1])
  qc.u3(theta[3], theta[4], theta[5], q[1])
  qc.cx(q[0], q[1])
  qc.u3(theta[6], theta[7], theta[8], q[1])
  qc.cx(q[1], q[2])
  qc.u3(theta[9], theta[10], theta[11], q[2])
  qc.measure(q[0], c[0])
  qc.measure(q[1], c[1])
  qc.measure(q[2], c[2])

predictions = []
for i in range(len(testing_set["prices"])):
  qc.data = [testing_set["prices"][i], testing_set["large_position_detected"][i], testing_set["dark_pool_order_detected"][i], testing_set["momentum"][i]]
  result = qc.run(backend)
  probability = result.get_counts()[0] / 100
  if probability > THRESHOLD:
    prediction = "UP"
  else:
    prediction = "DOWN"
  predictions.append(prediction)

for i in range(len(predictions)):
  if predictions[i] == "UP" and testing_set["prices"][i] < THRESHOLD:
    order = api.place_order(contract_id, 1, "buy", "market", "day")
    if order.status == "filled":
      send_email("Buy order filled for option contract ", contract_id)
  elif predictions[i] == "DOWN" and testing_set["prices"][i] > THRESHOLD:
    order = api.place_order(contract_id, 1, "sell", "market", "day")
    if order.status == "filled":
      send_email("Sell order filled for option contract ", contract_id)


