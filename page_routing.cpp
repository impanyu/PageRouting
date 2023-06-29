#include <vector>
#include <cmath>
#include <algorithm>
#include <random>
#include <map>

struct Point {
    std::vector<double> coordinates;
};

double distance(const Point& a, const Point& b) {
    double dist = 0.0;
    for (size_t i = 0; i < a.coordinates.size(); ++i) {
        double diff = a.coordinates[i] - b.coordinates[i];
        dist += diff * diff;
    }
    return std::sqrt(dist);
}

// Simple Graph-based ANN
class SimpleGraphANN {
private:
    std::vector<Point> points;
    std::map<int, std::vector<int>> graph;  // The adjacency list representation of the graph

public:
    SimpleGraphANN(const std::vector<Point>& points) : points(points) {
        // Construct the graph by linking each point to its closest other point
        for (int i = 0; i < points.size(); ++i) {
            double min_dist = std::numeric_limits<double>::max();
            int min_index = -1;

            // This is a naive way to build the graph and not how DiskANN does it.
            // DiskANN uses a more sophisticated method (like NN-Descent) to build the graph efficiently.
            for (int j = 0; j < points.size(); ++j) {
                if (i != j) {
                    double dist = distance(points[i], points[j]);
                    if (dist < min_dist) {
                        min_dist = dist;
                        min_index = j;
                    }
                }
            }
            graph[i].push_back(min_index);
        }
    }

    int query(const Point& query_point) {
        // Start from a random point in the dataset
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> distr(0, points.size() - 1);
        int current_point_index = distr(gen);

        // Perform the search
        while (true) {
            // Get the next point from the graph that is closer to the query point
            int next_point_index = *std::min_element(graph[current_point_index].begin(), graph[current_point_index].end(), 
                [&](int a, int b) {
                    return distance(query_point, points[a]) < distance(query_point, points[b]);
                });

            if (next_point_index == current_point_index) {
                break;
            }
            current_point_index = next_point_index;
        }

        // Return the closest point index
        return current_point_index;
    }
};
