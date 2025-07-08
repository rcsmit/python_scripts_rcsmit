from matplotlib import gridspec

import matplotlib.pyplot as plt
import numpy as np


# Data for the graph
stages = ['Opening', 'Build-Up', 'Peak Energy', 'Breakdown', 'Rebuild', 'Climax/Drop', 'Outro/Close']
energy = [2, 4, 8, 3, 5, 9, 2]  # Representing energy levels at each stage


# Creating a figure with two subplots
fig = plt.figure(figsize=(10, 10))
gs = gridspec.GridSpec(2, 1, height_ratios=[2, 3])

# First subplot: Infographic
ax1 = plt.subplot(gs[0])
ax1.text(0.5, 0.8, 'STAGES OF A TECHNO SET', fontsize=18, ha='center', fontweight='bold', color='white', bbox=dict(facecolor='orange', alpha=0.6))
ax1.text(0.5, 0.7, 'Opening | Atmospheric, deep build', fontsize=12, ha='center', color='orange')
ax1.text(0.5, 0.6, 'Build-Up | Gradual increase in energy, layering vocals and groove', fontsize=12, ha='center', color='orange')
ax1.text(0.5, 0.5, 'Peak Energy | Hypnotic rhythm, deep bassline, high energy', fontsize=12, ha='center', color='orange')
ax1.text(0.5, 0.4, 'Breakdown | Atmospheric, tension-building', fontsize=12, ha='center', color='orange')
ax1.text(0.5, 0.3, 'Rebuild | Gradual re-entry into rhythm, adding layers', fontsize=12, ha='center', color='orange')
ax1.text(0.5, 0.2, 'Climax/Drop | Intense, hypnotic drop with raw energy', fontsize=12, ha='center', color='orange')
ax1.text(0.5, 0.1, 'Outro/Close | Smooth fade, minimalistic closing', fontsize=12, ha='center', color='orange')
ax1.set_facecolor('darkgray')
ax1.axis('off')

# Second subplot: Energy Flow Graph
ax2 = plt.subplot(gs[1])
ax2.plot(stages, energy, marker='o', linestyle='-', color='orange', markersize=8)
ax2.set_xlabel('Stages of a Techno Set', fontsize=12)
ax2.set_ylabel('Energy Level', fontsize=12)
ax2.set_title('Energy Flow in a Techno Set', fontsize=14)
ax2.grid(True)

# Adjust layout
plt.tight_layout()
plt.show()
