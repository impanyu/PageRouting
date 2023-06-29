#include "point.hpp"

double distance(const point& a, const point& b) {
    double dist = 0.0;
    for (size_t i = 0; i < a.coordinates.size(); ++i) {
        double diff = a.coordinates[i] - b.coordinates[i];
        dist += diff * diff;
    }
    return std::sqrt(dist);
}
