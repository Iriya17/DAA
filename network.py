import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import json
import os

class NetworkDesignSystem:
    def __init__(self, budget=500000):
        self.locations = {}
        self.possible_connections = []
        self.parent = {}
        self.rank = {}
        self.total_budget = budget
        
    def add_location(self, name, location_type, devices_count, coordinates):
        """Add a network location (office/department)"""
        self.locations[name] = {
            'name': name,
            'type': location_type,
            'devices': devices_count,
            'coordinates': coordinates,
            'connections': [],
            'bandwidth_requirement': devices_count * 100
        }
        self.parent[name] = name
        self.rank[name] = 0
        
    def calculate_distance(self, coord1, coord2):
        """Calculate distance between two points"""
        return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)
        
    def add_possible_connection(self, loc1, loc2, cable_type):
        """Add possible network connection between locations"""
        distance = self.calculate_distance(
            self.locations[loc1]['coordinates'],
            self.locations[loc2]['coordinates']
        )
        
        cable_specs = {
            'fiber': {
                'cost_per_meter': 100,
                'bandwidth': 10000,
                'reliability': 0.99
            },
            'copper': {
                'cost_per_meter': 50,
                'bandwidth': 1000,
                'reliability': 0.95
            }
        }
        
        base_cost = distance * cable_specs[cable_type]['cost_per_meter']
        installation_cost = distance * 20
        total_cost = base_cost + installation_cost
        
        self.possible_connections.append({
            'locations': (loc1, loc2),
            'distance': distance,
            'cable_type': cable_type,
            'cost': total_cost,
            'bandwidth': cable_specs[cable_type]['bandwidth'],
            'reliability': cable_specs[cable_type]['reliability']
        })
        
    def find_parent(self, location):
        if self.parent[location] != location:
            self.parent[location] = self.find_parent(self.parent[location])
        return self.parent[location]
        
    def union_locations(self, loc1, loc2):
        root1 = self.find_parent(loc1)
        root2 = self.find_parent(loc2)
        
        if self.rank[root1] < self.rank[root2]:
            self.parent[root1] = root2
        elif self.rank[root1] > self.rank[root2]:
            self.parent[root2] = root1
        else:
            self.parent[root2] = root1
            self.rank[root1] += 1
            
    def design_optimal_network(self):
        """Apply Kruskal's algorithm to design optimal network"""
        sorted_connections = sorted(self.possible_connections, key=lambda x: x['cost'])
        optimal_design = []
        total_cost = 0
        total_cable_length = 0
        fiber_connections = 0
        copper_connections = 0
        
        for connection in sorted_connections:
            loc1, loc2 = connection['locations']
            
            if self.find_parent(loc1) != self.find_parent(loc2):
                if total_cost + connection['cost'] <= self.total_budget:
                    self.union_locations(loc1, loc2)
                    optimal_design.append(connection)
                    total_cost += connection['cost']
                    total_cable_length += connection['distance']
                    
                    if connection['cable_type'] == 'fiber':
                        fiber_connections += 1
                    else:
                        copper_connections += 1
                        
                    self.locations[loc1]['connections'].append(connection)
                    self.locations[loc2]['connections'].append(connection)
        
        return {
            'optimal_connections': optimal_design,
            'total_cost': total_cost,
            'total_cable_length': total_cable_length,
            'fiber_connections': fiber_connections,
            'copper_connections': copper_connections,
            'remaining_budget': self.total_budget - total_cost
        }

    def visualize_network(self, design):
        """Visualize the network design with detailed metrics"""
        plt.figure(figsize=(12, 8))

        # Plot locations
        for name, loc in self.locations.items():
            x, y = loc['coordinates']
            color = 'red' if 'Server' not in name else 'blue'
            plt.plot(x, y, 'o', color=color, markersize=10)
            plt.annotate(name, (x, y), xytext=(5, 5), textcoords='offset points')

        # Plot connections with additional details
        for conn in design['optimal_connections']:
            loc1, loc2 = conn['locations']
            x1, y1 = self.locations[loc1]['coordinates']
            x2, y2 = self.locations[loc2]['coordinates']

            color = 'green' if conn['cable_type'] == 'fiber' else 'orange'
            plt.plot([x1, x2], [y1, y2], color=color, linestyle='-', linewidth=2)

            # Calculate mid-point for annotation
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            plt.text(mid_x, mid_y, f"{conn['bandwidth']} Mbps\n${conn['cost']:,.2f}",
                     fontsize=8, ha='center', color='black', backgroundcolor='white', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        plt.title('Network Design Visualization')
        plt.grid(True)
        plt.axis('equal')  # To maintain the aspect ratio
        plt.legend()
        plt.show()

    def save_design(self, filename="graph_data.json"):
        """Save the current design to a file"""
        with open(filename, 'w') as f:
            json.dump(self.possible_connections, f)
        
    def load_design(self):
        """Load a design from a file"""
        if os.path.exists("graph_data.json"):
            with open("graph_data.json", 'r') as f:
                self.possible_connections = json.load(f)
            return True
        return False

class Network:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Design System")
        self.root.geometry("600x500")
        self.root.configure(bg="#C6E7FF")  # Set a light background color
        self.network = NetworkDesignSystem()
        self.last_design = None  # Store last generated design
        self.setup_gui()
        
    def setup_gui(self):
        # Create frames
        input_frame = ttk.LabelFrame(self.root, text="Add Location", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Location input fields
        ttk.Label(input_frame, text="Location Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Type:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar()
        types = ['Server', 'Office', 'Department', 'Laboratory']
        ttk.Combobox(input_frame, textvariable=self.type_var, values=types).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Devices Count:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=5)
        self.devices_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.devices_var).grid(row=2, column=1, padx=5, pady=5)

        # Budget input field
        ttk.Label(input_frame, text="Set Budget:", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=5, pady=5)
        self.budget_var = tk.StringVar(value="500000")
        ttk.Entry(input_frame, textvariable=self.budget_var).grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        ttk.Button(input_frame, text="Add Location", command=self.add_location).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(input_frame, text="Generate Design", command=self.generate_design).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(input_frame, text="Show Visualization", command=self.show_visualization).grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(input_frame, text="Save Design", command=self.save_design).grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(input_frame, text="Load Design", command=self.load_design).grid(row=8, column=0, columnspan=2, pady=10)

        # Output message label
        self.output_label = ttk.Label(self.root, text="", font=("Arial", 10, "bold"), background="#f0f0f0")
        self.output_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    def add_location(self):
        name = self.name_var.get()
        location_type = self.type_var.get()
        devices_count = int(self.devices_var.get())
        coordinates = (random.randint(0, 100), random.randint(0, 100))  # Random coordinates
        self.network.add_location(name, location_type, devices_count, coordinates)
        self.output_label.config(text=f"Added {location_type} '{name}' with {devices_count} devices.", anchor="center")

    def generate_design(self):
        budget = int(self.budget_var.get())
        self.network.total_budget = budget
        locations = list(self.network.locations.keys())
        
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                cable_type = random.choice(['fiber', 'copper'])
                self.network.add_possible_connection(locations[i], locations[j], cable_type)
        
        self.last_design = self.network.design_optimal_network()  # Store the generated design
        self.output_label.config(text=f"Design generated with total cost: ${self.last_design['total_cost']:,.2f}", anchor="center")
        
    def show_visualization(self):
        if self.last_design is None:
            messagebox.showwarning("Warning", "Please generate a design first.")
            return
        self.network.visualize_network(self.last_design)  # Use the stored design

    def save_design(self):
        self.network.save_design()

    def load_design(self):
        if self.network.load_design():
            self.output_label.config(text="Design loaded successfully!", anchor="center")
        else:
            self.output_label.config(text="Failed to load design.", anchor="center")

if __name__ == "__main__":
    root = tk.Tk()
    app = Network(root)
    root.mainloop()
