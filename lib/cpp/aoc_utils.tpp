#include <map>
#include <vector>
#include <concepts>

////////////////////////////////////////////////////////////////////////////////
namespace aoc_utils {
////////////////////////////////////////////////////////////////////////////////

template <std::integral T>
size_t uz(T index) {
    return static_cast<size_t>(index);
}

template<typename Key, typename CountType = int64_t>
class Counter {
  private:
    std::map<Key, CountType> counts_;
  public:
    Counter() = default;

    explicit Counter(const std::vector<Key>& elements) {
        update(elements);
    }

    /**
     * Access count of element (const)
     * @param key Element to look up
     * @return Count of element (0 if not present)
     */
    CountType operator[](const Key& key) const {
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
    CountType& operator[](const Key& key) {
        return counts_[key];
    }

    /**
     * Modify count of elements
     * @param elements Elements to increment
     */
    void update(const std::vector<Key>& elements) {
        for (const Key& e : elements) {
            counts_[e]++;
        }
    }
};

////////////////////////////////////////////////////////////////////////////////
}
