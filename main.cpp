#include <vector>
#include <cmath>
#include <algorithm>
#include <random>
#include <map>
#include <iostream>

struct Point {
    std::vector<double> coordinates;
};

double distance(const Point& a, const Point& b) {
    // ... existing code ...
}

class SimpleGraphANN {
    // ... existing code ...
};

int main() {
    // Create a vector of points
    std::vector<Point> points;
    
    // Fill the vector with random points
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> distr(-100.0, 100.0);
    
    for (int i = 0; i < 1000; ++i) {
        Point point;
        for (int j = 0; j < 10; ++j) {  // Create 10-dimensional points
            point.coordinates.push_back(distr(gen));
        }
        points.push_back(point);
    }
    
    // Create the SimpleGraphANN
    SimpleGraphANN ann(points);

    // Generate a random query point
    Point query_point;
    for (int j = 0; j < 10; ++j) {
        query_point.coordinates.push_back(distr(gen));
    }

   // Query the closest point
    int closest_point_index = ann.query(query_point);
    std::cout << "The index of the closest point to the query is: " << closest_point_index << std::endl;

    return 0;
}