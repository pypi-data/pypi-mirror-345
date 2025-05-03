# scripts/print_ethnicities.py

from ethnicities import all_ethnicities, common, by_region, common_and_by_region

if __name__ == "__main__":
    print("------------------------ All Ethnicities:")

    for eth in all_ethnicities:
        print(eth)
    print()
    
    print("------------------------ Common Ethnicities:")
    for eth in common:
        print(eth)
    print()

    print("------------------------ By Region:")
    for region, items in by_region.items():
        print(region + ":")
        for eth in items:
            print(eth)
        print()

    print("------------------------ Common and by Region:")
    for region, items in common_and_by_region.items():
        print(region + ":")
        for eth in items:
            print(eth)
        print()
