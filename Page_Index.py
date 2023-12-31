import numpy as np
import heapq
import json
import networkx as nx
import random
import os


class Node:
    def __init__(self, vector, node_id,page_index, max_neighbors=50, alpha=1.2):
        self.vector = vector #list of floating point numbers
        self.node_id = node_id
        self.max_neighbors = max_neighbors
        self.neighbor_ids = []
        self.alpha = alpha
        self.page_index = page_index

    def add_neighbor(self, new_neighbor_id):
        self.neighbor_ids.append(new_neighbor_id)
        if len(self.neighbor_ids) > self.max_neighbors:
            self.prune_neighbors()

    def add_neighbors(self, new_neighbor_ids):
        self.neighbor_ids = self.neighbor_ids + new_neighbor_ids
        if self.neighbor_ids > self.max_neighbors:
            self.prune_neighbors()

    def find_nearest_neighbors(self):

        priority_queue = []
        for neighbor_id in self.neighbor_ids:
            neighbor = self.page_index.get_node(neighbor_id)
            if neighbor is None:
                continue
            distance = self.distance(neighbor.get_vector())
            heapq.heappush(priority_queue, (distance, neighbor_id))
        distance, nearest_neighbor_id = heapq.heappop(priority_queue)
    
    #TODO to be implemented
    def prune_neighbors(self):
        neighbor_ids = []
        while len(self.neighbor_ids) > 0:
            distance, nearest_neighbor_id = self.find_nearest_neighbors()
            nearest_neighbor = self.page_index.get_node(nearest_neighbor_id)
            neighbor_ids.append(nearest_neighbor_id)
            if len(neighbor_ids) >= self.max_neighbors:
                break

            for i in range(len(self.neighbor_ids)-1,-1,-1):
                neighbor_id = self.neighbor_ids[i]
                neighbor = self.get_node(neighbor_id)
                if neighbor is None:
                    self.neighbor_ids.remove(neighbor_id)
                    continue

                distance_1 = nearest_neighbor.distance(neighbor.get_vector())
                distance_2 = self.distance(neighbor.get_vector())

                if self.alpha * distance_1 < distance_2:
                    self.neighbor_ids.remove(neighbor_id)
     
  
        self.neighbor_ids = neighbor_ids

    def remove_neighbor(self, neighbor_id):
        if neighbor_id in self.neighbor_ids:
            self.neighbor_ids.remove(neighbor_id)
        
    def get_neighbor_ids(self):
        return self.neighbor_ids
    
    def get_vector(self):
        return self.vector
    
    def get_id(self):
        return self.node_id
    
    def distance(self, other_vector):
        return np.linalg.norm(np.array(self.vector) - np.array(other_vector))
    

class Page:
    def __init__(self, nodes_per_page, page_id=None):       
        self.nodes_per_page = nodes_per_page
        self.nodes = []
        self.page_id = page_id

    def add_node(self, new_node):
        self.nodes.append(new_node)
   

    def add_nodes(self, new_nodes):
        self.nodes = self.nodes + new_nodes

    def merge_page(self, page):
        for node in page.get_nodes():
            self.add_node(node)

    # this function splits the page into two pages and returns the new page
    def split_page(self):
        G = nx.DiGraph()
        node_ids = [node.get_id() for node in self.nodes]
        G.add_nodes_from(node_ids)
        for node in self.nodes:
            for neighbor_id in node.get_neighbor_ids():
                if neighbor_id in node_ids:
                    G.add_edge(node.get_id(), neighbor_id)
        # Use the Kernighan–Lin algorithm to partition the graph into two parts
        partition = nx.algorithms.community.kernighan_lin_bisection(G)

        # Unpack the two parts
        part1, part2 = partition

        nodes_1 = [node for node in self.nodes if node.get_id() in part1]
        nodes_2 = [node for node in self.nodes if node.get_id() in part2]

        self.nodes = nodes_1
        new_page = Page(self.nodes_per_page)
        new_page.add_nodes(nodes_2)

        return new_page

    def remove_node(self, node):
        self.nodes.remove(node)

    def get_nodes(self):
        return self.nodes
    
    def get_id(self):
        return self.page_id
    
    def get_node_by_id(self,node_id):
        for node in self.nodes:
            if node.get_id() == node_id:
                return node
        return None




class Page_Index:
    def __init__(self, dim, max_neighbors, index_file, meta_data_file, k=5, L=50, max_visits=1000, nodes_per_page=20, page_buffer_size=100, max_ios_per_hop = 3):
        self.k = k
        self.L = L
        self.max_visits = max_visits
        self.dim = dim
        self.max_neighbors = max_neighbors

        self.index_file = index_file
        self.meta_data_file = meta_data_file

        self.nodes_per_page = nodes_per_page
        self.number_of_pages = 0

        self.node_ids = {}
        self.page_buffers = []

        self.changed_pages = {}

        self.page_buffers_size = page_buffer_size

        self.page_size = (self.nodes_per_page * (self.dim+self.max_neighbors+1))* 4

        self.max_ios_per_hop = max_ios_per_hop

        try:
            if os.path.exists(self.meta_data_file):
                with open(self.meta_data_file, 'r') as f:
                    
                    self.meta_data = json.load(f)
                    self.node_ids = self.meta_data['node_ids']
                    self.available_page_ids = self.meta_data['available_page_ids']
                    self.available_node_ids = self.meta_data['available_node_ids']
            else:
                self.node_ids = {}
                self.available_page_ids = [0]
                self.available_node_ids = [0]
                self.meta_data = {'node_ids':self.node_ids, 'available_page_ids':self.available_page_ids, 'available_node_ids':self.available_node_ids}
                with open(self.meta_data_file, 'w') as f:
                    json.dump(self.meta_data, f)

                with open(self.index_file, 'wb') as f:
                    f.write(np.array([]).tobytes())

        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_page(self,page_id):
        self.available_page_ids.insert(0,page_id)
                

    def get_available_page_id(self):
        if len(self.available_page_ids) == 0:
            self.available_page_ids[0] += 1
            return self.available_page_ids[0] - 1
        else:
            return self.available_page_ids.pop(0)
            

    def get_aviailable_node_id(self):
        if len(self.available_node_ids) == 0:
            self.available_node_ids[0] += 1
            return self.available_node_ids[0] - 1
        else:
            return self.available_node_ids.pop(0)

    #find best page to insert the node
    def find_best_page(self, node):
        page_co_located_counts = {}
        for neighbor_id in node.get_neighbor_ids():
            
            neighbor = self.get_node(neighbor_id)
            if not neighbor:
                continue
            neighbor_page_id = self.node_ids[neighbor_id]
            page_co_located_counts[neighbor_page_id] = page_co_located_counts.get(neighbor_page_id, 0) + 1
            if node.get_id() in neighbor.get_neighbor_ids():
                page_co_located_counts[neighbor_page_id] = page_co_located_counts.get(neighbor_page_id, 0) + 1
        
        max_page_co_located_count = 0
        for page_id in page_co_located_counts.keys():
            page_co_located_count = page_co_located_counts[page_id]
            if page_co_located_count > max_page_co_located_count:
                max_page_co_located_count = page_co_located_count
                best_page_id = page_id
        
        return self.get_page(best_page_id)
                
            
    def merge_pages(self, page1, page2):
        page1.merge_page(page2)
        self.delete_page(page2.get_id())
        self.changed_pages[page1.get_id()]=page1

    def dump_changed_pages(self):
        for page_id in self.changed_pages:
            page = self.changed_pages[page_id]
            with open(self.index_file, 'rb+') as f:
                f.seek(page_id *self.page_size)
                for node in page.get_nodes():
                    node_data = np.append([node.get_id()], node.get_vector())
                    node_data = np.append(node_data,node.get_neighbor_ids())
                    f.write(node_data.astype(np.float32).tobytes())
                # padding with zeros
                if len(page.get_nodes()) < self.nodes_per_page:
                    f.write(np.zeros(int(self.page_size/4) - len(page.get_nodes())*(self.dim+self.max_neighbors+1)).astype(np.float32).tobytes())

        self.changed_pages = {}

    def dump_meta_data(self):
        with open(self.meta_data_file, 'w') as f:
            json.dump(self.meta_data, f)


    def get_page(self,page_id):
        for page in self.page_buffers: 
            if page_id == page.get_id():
                return page
        
        return self.get_page_from_file(page_id)
    

    def get_page_from_file(self, page_id):
        
        with open(self.index_file, 'rb') as f:
            # index_file is a binary file, so we need to seek to the correct position
            f.seek(page_id *self.page_size)
            # read the page from the file
            try:
                page_data = np.fromfile(f, dtype=np.float32, count=int(self.page_size/4))
            except Exception as e:
                return None
        
        page = Page(self.nodes_per_page, page_id)

        for i in range(self.nodes_per_page):
            node_data = page_data[i*(self.dim+self.max_neighbors+1):(i+1)*(self.dim+self.max_neighbors+1)]
            node_id = int(node_data[0])
            vector = list(node_data[1:self.dim])
            node_neighbors = list(node_data[self.dim:].astype(np.int32))
            if node_id == -1:
                break

            node = Node(vector, int(node_id),self, self.max_neighbors)
            node.add_neighbors(node_neighbors)

            page.add_node(node)

        self.page_buffers.append(page)
        if len(self.page_buffers) > self.page_buffers_size:
            self.page_buffers.pop(0)

        return page
    
    def get_node(self, node_id):
        if node_id not in self.node_ids:
            return None
        page_id = self.node_ids[node_id]
        page = self.get_page(page_id)
        return page.get_node_by_id(node_id)

    def insert_node(self, vector):
        rand_idx = random.randint(0,len(self.node_ids))
        start_node_id = list(self.node_ids.keys())[rand_idx]
   
        #start_node = self.get_node(start_node)

        top_k_node_ids,visited_node_ids = self.search(vector, start_node_id, self.k, self.L, self.max_visits)

        new_node_id = self.get_aviailable_node_id()

        new_node = Node(vector, new_node_id, self, self.max_neighbors)

        new_node.add_neighbors(visited_node_ids)

        best_page = self.find_best_page(new_node)

        best_page.add_node(new_node)

        self.changed_pages[best_page.get_id()] = best_page

        # split page if necessary
        if len(best_page.get_nodes()) > self.nodes_per_page:
            new_page = best_page.split_page()
            self.number_of_pages += 1
            new_page_id = self.get_available_page_id()
            new_page.page_id = new_page_id
            self.page_buffers.append(new_page)
            self.changed_pages[new_page_id] = new_page

            for node in new_page.get_nodes():
                self.node_ids[node.get_id()] = new_page_id
            
            for node in best_page.get_nodes():
                self.node_ids[node.get_id()] = best_page.get_id()

        self.node_ids[new_node_id] = best_page.get_id()

        # add the new node to the neighbor list of the neighbors
        for neighbor_id in new_node.get_neighbor_ids():
            neighbor = self.get_node(neighbor_id)
            neighbor_page_id = self.node_ids[neighbor_id]
            if neighbor:
                neighbor.add_neighbor(new_node_id)
                self.changed_pages[neighbor_page_id] = self.get_page(neighbor_page_id)



   
    #in some case delete_node may not delete the link pointing to the deleted node, so deleted node may still be in the neighbor list of other nodes
    def delete_node(self, node_id):
        if node_id not in self.node_ids:
            return 
        page_id = self.node_ids[node_id]
        page = self.get_page(page_id)
        node = page.get_node_by_id(node_id)
        page.remove_node(node)
        self.changed_pages[page_id] = page
        self.node_ids.pop(node_id,None)
        self.available_node_ids.insert(0,node_id)

        # iterate through all the neighbors of the node and remove the node from their neighbor list
        # also add the neighbors of the node to the neighbor list of the neighbors to perserve the links: when a->delete_node and delete_node -> b, we add a->b
        for neighbor_id in node.get_neighbor_ids():
            neighbor = self.get_node(neighbor_id)
            if not neighbor:
                continue
            neighbor_page = self.get_page(self.node_ids[neighbor_id])
            
            if node_id in neighbor.get_neighbor_ids():
                neighbor.remove_neighbor(node_id)
                other_neighbor_ids =[other_neighbor_id for other_neighbor_id in node.get_neighbor_ids() if other_neighbor_id != neighbor_id]
                neighbor.add_neighbors(other_neighbor_ids)
            
                self.changed_pages[self.node_ids[neighbor_id]] = neighbor_page

     
           
    def search(self, query_vector, start_node_id, k, L, max_visits):
        # This priority queue will keep track of nodes to visit
        # Format is (distance, node)
        start_node = self.get_node(start_node_id)
        dis = start_node.get_distance(query_vector)
        to_visit = [(dis, start_node_id)]
        visited = set() # Keep track of visited nodes


        num_visits = 0

        while to_visit and num_visits < max_visits:
            distance, current_node_id = heapq.heappop(to_visit)
            
            # If we've already visited this node, continue
            if current_node_id in visited:
                continue

            # Mark this node as visited
            visited.add(current_node_id)

            current_node = self.get_node(current_node_id)

            ioed_pages = set()

            # Add neighbors to the to_visit queue
            neighbor_ids = current_node.get_neighbor_ids()

            for neighbor_id in neighbor_ids:
                if neighbor_id not in visited:
                    continue
                if neighbor_id not in self.node_ids:
                    continue
                neighbor_page_id = self.node_ids[neighbor_id]
                ioed_pages.add(neighbor_page_id)
                if len(ioed_pages) > self.max_ios_per_hop:
                    break

                neighbor_node = self.get_node(neighbor_id)
                neighbor_distance = neighbor_node.get_distance(query_vector)
                heapq.heappush(to_visit, (neighbor_distance, neighbor_id))

            if len(to_visit) > L:
                top_L = [heapq.heappop(to_visit) for _ in range(L)]
                to_visit = top_L
            

            num_visits += 1

        return [heapq.heappop(to_visit)[1] for _ in range(k)],visited




if __name__ == '__main__':

    page_index = Page_Index(100, 50, 'index.bin', 'node_ids.json')
    #load data from hdf5 file




    # Example usage
    vectors = np.array([...]) # Your input vectors
    graph = construct_graph(vectors)
    query_vector = np.array([...]) # Your query vector
    nearest_neighbors = greedy_search(graph, query_vector)



