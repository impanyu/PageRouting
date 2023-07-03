#include <vector>
#include <cmath>


#include "point.hpp"


class page {
private:
    std::vector<point> points; // The array of points in the page

public:

    page(){};

    bool insert(const point& point);

    void remove(const point& removed_point);

    int query(const point& query_point);
};
