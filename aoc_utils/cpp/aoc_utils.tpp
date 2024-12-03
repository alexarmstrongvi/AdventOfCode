#include <map>
#include <vector>

////////////////////////////////////////////////////////////////////////////////
namespace aoc_utils {
////////////////////////////////////////////////////////////////////////////////

template<typename T>
class Counter {
  private:
    std::map<T, size_t> counts_;
  public:
    Counter() = default;

    explicit Counter(const std::vector<T>& elements) {
        update(elements);
    }

    /**
     * Access count of element (const)
     * @param key Element to look up
     * @return Count of element (0 if not present)
     */
    size_t operator[](const T& key) const {
        auto it = counts_.find(key);
        if (it == counts_.end()) {
            return 0;
        }
        return it->second;
    }

    /**
     * Access or modify count of element
     * @param key Element to look up/modify
     * @return Reference to count for element
     */
    size_t& operator[](const T& key) {
        return counts_[key];
    }

    /**
     * Modify count of elements
     * @param elements Elements to increment
     */
    void update(const std::vector<T>& elements) {
        for (const T& e : elements) {
            counts_[e]++;
        }
    }
};

////////////////////////////////////////////////////////////////////////////////
}
