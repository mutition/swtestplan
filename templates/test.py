import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Define labels
prob_labels = ["Low", "Moderate", "Significant", "High"]
impact_labels = ["High", "Significant", "Moderate", "Low"]

# Create figure and axes
fig, ax = plt.subplots(figsize=(6, 6))

# Draw grid and shade cells for risks
# Mapping: (probability_index, impact_index)
risks = {
    "R6": (1, 0),  # Moderate probability, High impact
    "R1": (3, 0),  # High probability, High impact
    "R4": (3, 2),  # High probability, Moderate impact
    "R2, R3, R5": (2, 1)  # Significant probability, Significant impact
}

# Draw cells and labels
for col in range(4):
    for row in range(4):
        # Shade if a risk is here
        for label, (c, r) in risks.items():
            if col == c and row == r:
                ax.add_patch(Rectangle((col, row), 1, 1, alpha=0.3))
        # Draw cell border
        ax.add_patch(Rectangle((col, row), 1, 1, fill=False, edgecolor='black'))

# Add risk annotations
for label, (c, r) in risks.items():
    ax.text(c + 0.5, r + 0.5, label, ha='center', va='center')

# Draw tolerance lines
# Horizontal between High and Significant impact (y=1)
ax.plot([0, 4], [1, 1], color='black', linewidth=2)
# Vertical between Moderate and Significant probability (x=2)
ax.plot([2, 2], [0, 4], color='black', linewidth=2)

# Set ticks and labels
ax.set_xticks([0.5, 1.5, 2.5, 3.5])
ax.set_xticklabels(prob_labels)
ax.set_yticks([0.5, 1.5, 2.5, 3.5])
ax.set_yticklabels(impact_labels)

# Invert y-axis to have 'High' at top
ax.invert_yaxis()

# Labels and title
ax.set_xlabel("Probability")
ax.set_ylabel("Impact")
ax.set_title("Risk Exposure Matrix")

plt.tight_layout()
plt.show()