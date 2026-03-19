import matplotlib.pyplot as plt

rates4 = [0.0, 0.25, 0.5, 0.75, 0.9]
times4 = [0.101, 0.109, 0.139, 0.190, 0.388]

rates5 = [0.0, 0.25, 0.5, 0.75, 0.9]
times5 = [0.098, 0.15, 0.22, 0.30, 0.50]  

plt.plot(rates4, times4, marker='o', label="ACK Loss (Option 4)")
plt.plot(rates5, times5, marker='o', label="DATA Loss (Option 5)")

plt.xlabel("Loss Rate")
plt.ylabel("Completion Time (seconds)")
plt.title("Completion Time vs Loss Rate")

plt.legend()
plt.grid()

plt.savefig("phase3_plot.png")
plt.show()
