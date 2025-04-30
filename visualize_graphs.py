import os
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import math

class GraphVisualizer:
    def __init__(self, graphs_folder):
        self.graphs_folder = graphs_folder
        self.graph_files = [f for f in os.listdir(graphs_folder) if f.endswith('.txt')]
        self.figures = []
        
    def read_graph(self, filename):
        """Read graph data from file"""
        with open(os.path.join(self.graphs_folder, filename), 'r') as f:
            # Read graph name
            graph_name = f.readline().strip()
            
            # Read number of nodes
            num_nodes = int(f.readline().strip())
            
            # Read coordinates
            coordinates = []
            for _ in range(num_nodes):
                x, y = map(float, f.readline().strip().split())
                coordinates.append((x, y))
            
            # Read start and goal nodes
            start_node, goal_node = map(int, f.readline().strip().split())
            
            # Read number of edges
            num_edges = int(f.readline().strip())
            
            # Read edges
            edges = []
            for _ in range(num_edges):
                u, v, w = map(float, f.readline().strip().split())
                edges.append((int(u), int(v), w))
            
            return {
                'name': graph_name,
                'num_nodes': num_nodes,
                'coordinates': coordinates,
                'start_node': start_node,
                'goal_node': goal_node,
                'edges': edges
            }
    
    def visualize_graph(self, graph_data, filename):
        """Visualize the graph using matplotlib"""
        # Create a new figure for each graph
        fig, ax = plt.subplots(figsize=(10, 8))
        self.figures.append(fig)
        
        # Create a NetworkX graph
        G = nx.Graph()
        
        # Add nodes with positions
        pos = {}
        for i in range(graph_data['num_nodes']):
            G.add_node(i)
            pos[i] = graph_data['coordinates'][i]
        
        # Add edges
        for u, v, w in graph_data['edges']:
            G.add_edge(int(u), int(v), weight=w)
        
        # Set node colors
        node_colors = ['lightblue'] * graph_data['num_nodes']
        node_colors[graph_data['start_node']] = 'green'
        node_colors[graph_data['goal_node']] = 'red'
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=500, alpha=0.8, ax=ax)
        
        nx.draw_networkx_edges(G, pos, width=1.0, ax=ax)
        
        # Draw edge labels
        edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
        
        # Draw node labels
        labels = {i: str(i) for i in range(graph_data['num_nodes'])}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, 
                               font_weight='bold', ax=ax)
        
        # Set up proper coordinate system
        # Get min and max coordinates to set axis limits with some padding
        x_coords = [coord[0] for coord in graph_data['coordinates']]
        y_coords = [coord[1] for coord in graph_data['coordinates']]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # Add 10% padding
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.1
        
        # Set axis limits
        ax.set_xlim(x_min - x_padding, x_max + x_padding)
        ax.set_ylim(y_min - y_padding, y_max + y_padding)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Show axes with ticks and labels
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        
        # Create more readable tick marks with specific values
        # Round to nearest 5 or 10 for cleaner numbers
        def get_nice_ticks(min_val, max_val, num_ticks=8):
            # Determine a nice step size
            range_val = max_val - min_val
            if range_val <= 20:
                step = max(1, round(range_val / num_ticks))
            elif range_val <= 50:
                step = max(5, round(range_val / num_ticks / 5) * 5)
            else:
                step = max(10, round(range_val / num_ticks / 10) * 10)
            
            # Generate ticks
            start = math.floor(min_val / step) * step
            ticks = [start + i * step for i in range(int((max_val - start) / step) + 2)]
            return [t for t in ticks if min_val - step <= t <= max_val + step]
        
        # Set custom ticks
        x_ticks = get_nice_ticks(x_min, x_max)
        y_ticks = get_nice_ticks(y_min, y_max)
        
        ax.set_xticks(x_ticks)
        ax.set_yticks(y_ticks)
        
        # Make tick labels more visible
        ax.tick_params(axis='both', which='major', labelsize=10, width=1.5, length=6)
        
        # Format tick labels to be more readable
        if max(x_ticks) >= 100 or min(x_ticks) <= -100:
            ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
        else:
            ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
            
        if max(y_ticks) >= 100 or min(y_ticks) <= -100:
            ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
        else:
            ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
        
        # Set title and axis properties
        ax.set_title(f"Graph: {graph_data['name']}\nFile: {filename}\nStart: {graph_data['start_node']}, Goal: {graph_data['goal_node']}")
        
        # Add a legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=15, label='Start Node'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=15, label='Goal Node'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=15, label='Regular Node')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
    def run(self):
        """Run the visualization"""
        if not self.graph_files:
            print("No graph files found in the folder.")
            return
        
        print(f"Found {len(self.graph_files)} graph files in {self.graphs_folder}")
        
        # Create a separate window for each graph
        for i, filename in enumerate(self.graph_files):
            print(f"Visualizing graph {i+1}/{len(self.graph_files)}: {filename}")
            graph_data = self.read_graph(filename)
            self.visualize_graph(graph_data, filename)

        # Try to arrange windows in a more compatible way
        try:
            # Try to tile the windows if possible
            manager = plt.get_current_fig_manager()
            if hasattr(manager, 'window'):
                # Different backends have different methods
                if hasattr(manager.window, 'showNormal'):
                    manager.window.showNormal()
                elif hasattr(manager, 'frame'):
                    manager.frame.Maximize(False)
        except Exception as e:
            # If window management fails, just continue
            print(f"Note: Window management not supported on this system: {e}")
        
        # Show all figures
        plt.show()

if __name__ == "__main__":
    graphs_folder = "graphs"
    visualizer = GraphVisualizer(graphs_folder)
    visualizer.run()