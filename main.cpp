#include <vector>
#include <cmath>
#include <algorithm>
#include <random>
#include <map>
#include <iostream>

#include "include/page_rounting.hpp"

#include "include/point.hpp"



int main() {
    // Create a vector of points
    std::vector<point> points;
    
    // Fill the vector with random points
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> distr(-100.0, 100.0);
    
    for (int i = 0; i < 1000; ++i) {
        point point;
        for (int j = 0; j < 10; ++j) {  // Create 10-dimensional points
            point.coordinates.push_back(distr(gen));
        }
        points.push_back(point);
    }
    
    // Create the SimpleGraphANN
    page_routing ann(points);

    // Generate a random query point
    point query_point;
    for (int j = 0; j < 10; ++j) {
        query_point.coordinates.push_back(distr(gen));
    }

   // Query the closest point
    int closest_point_index = ann.query(query_point);
    std::cout << "The index of the closest point to the query is: " << closest_point_index << std::endl;

    return 0;
}