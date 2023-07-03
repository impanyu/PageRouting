#include <vector>

class point {
public:
    point(const std::vector<double>& coordinates, int max_pages){
        this-> coordinates = coordinates;
        this->page_pointers = std::vector<int>(max_pages,-1);

    }

    std::vector<double> coordinates;
    std::vector<int> page_pointers;
};