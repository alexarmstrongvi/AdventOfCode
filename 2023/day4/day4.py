import sys

def main():
    card_points = []
    card_counts = []
    for card_idx, line in enumerate(open(sys.argv[1])):
        line = line.strip()
        
        if card_idx >= len(card_counts):
            card_counts.append(0)
        card_counts[card_idx] += 1
        
        _, nums = line.split(':', 1)
        winning_nums, card_nums = nums.split('|', 1)
        winning_nums = set(int(num) for num in winning_nums.split())
        card_nums    = set(int(num) for num in card_nums.split())
        n_winning_nums = len(winning_nums & card_nums)

        # Part 1
        points = 2**(n_winning_nums-1) if n_winning_nums > 0 else 0
        card_points.append(points)
         
        # Part 2
        for i in range(n_winning_nums):
            idx = card_idx + i + 1
            if idx >= len(card_counts):
                card_counts.append(0)
            card_counts[idx] += card_counts[card_idx]
            
    for card_num, (points, count) in enumerate(zip(card_points,card_counts),1):
        print(f"INFO | Card {card_num}: {points} points; {count} cards")

    assert len(card_points) == len(card_counts)
    print("INFO | Part 1 solution:", sum(card_points))
    print("INFO | Part 2 solution:", sum(card_counts))

if __name__ == "__main__":
    main()

