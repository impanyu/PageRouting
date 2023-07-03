#include <vector>
#include <cmath>
#include <algorithm>
#include <random>
#include <map>

#include "point.hpp"


class page_routing {
private:
    std::vector<point> points;
    std::map<int, std::vector<int>> graph;  // The adjacency list representation of the page graph

public:
    page_routing(const std::vector<point>& points);

    page_routing(){};

    bool insert(const point& query_point);

    void remove(const point& removed_point);

    int query(const point& query_point);
};
