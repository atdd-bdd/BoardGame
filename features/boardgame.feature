Feature: Game

  Scenario: Setup Ship Happy Path
    Given my ships are
      | Type       | Length | Status     | Location | Orientation |
      | Carrier    | 5      | Not Placed |          |             |
      | Battleship | 4      | Not Placed |          |             |
      | Cruiser    | 3      | Not Placed |          |             |
      | Submarine  | 3      | Not Placed |          |             |
      | Destroyer  | 2      | Not Placed |          |             |
    When placed
      | Ship        | Carrier    |
      | Location    | 1,1        |
      | Orientation | Horizontal |
    Then my ships are now
      | Type       | Length | Status     | Location | Orientation |
      | Carrier    | 5      | Placed     | 1,1      | Horizontal  |
      | Battleship | 4      | Not Placed |          |             |
      | Cruiser    | 3      | Not Placed |          |             |
      | Submarine  | 3      | Not Placed |          |             |
      | Destroyer  | 2      | Not Placed |          |             |
    When placed
      | Ship        | Battleship |
      | Location    | 2,1        |
      | Orientation | Horizontal |
    When placed
      | Ship        | Cruiser    |
      | Location    | 3,1        |
      | Orientation | Horizontal |
    When placed
      | Ship        | Submarine  |
      | Location    | 4,1        |
      | Orientation | Horizontal |
    When placed
      | Ship        | Destroyer  |
      | Location    | 1,7        |
      | Orientation | Horizontal |
    Then my ships are now
      | Type       | Length | Status | Location | Orientation |
      | Carrier    | 5      | Placed | 1,1      | Horizontal  |
      | Battleship | 4      | Placed | 2,1      | Horizontal  |
      | Cruiser    | 3      | Placed | 3,1      | Horizontal  |
      | Submarine  | 3      | Placed | 4,1      | Horizontal  |
      | Destroyer  | 2      | Placed | 1,7      | Horizontal  |
    Then my ship display is now
      |    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
      | 1  | A | A | A | A | A |   | D | D |   |    |
      | 2  | B | B | B | B |   |   |   |   |   |    |
      | 3  | C | C | C |   |   |   |   |   |   |    |
      | 4  | S | S | S |   |   |   |   |   |   |    |
      | 5  |   |   |   |   |   |   |   |   |   |    |
      | 6  |   |   |   |   |   |   |   |   |   |    |
      | 7  |   |   |   |   |   |   |   |   |   |    |
      | 8  |   |   |   |   |   |   |   |   |   |    |
      | 9  |   |   |   |   |   |   |   |   |   |    |
      | 10 |   |   |   |   |   |   |   |   |   |    |
    Then game is
      | Status        | Winner |
      | Ready to Play | TBD    |

  Scenario: Some hits and misses
    Given my ships are
      | Type       | Length | Status | Location | Orientation |
      | Carrier    | 5      | Placed | 1,1      | Horizontal  |
      | Battleship | 4      | Placed | 2,1      | Horizontal  |
      | Cruiser    | 3      | Placed | 3,1      | Horizontal  |
      | Submarine  | 3      | Placed | 4,1      | Horizontal  |
      | Destroyer  | 2      | Placed | 1,7      | Horizontal  |
    Given my ship display is
      |    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
      | 1  | A | A | A | A | A |   | D | D |   |    |
      | 2  | B | B | B | B |   |   |   |   |   |    |
      | 3  | C | C | C |   |   |   |   |   |   |    |
      | 4  | S | S | S |   |   |   |   |   |   |    |
      | 5  |   |   |   |   |   |   |   |   |   |    |
      | 6  |   |   |   |   |   |   |   |   |   |    |
      | 7  |   |   |   |   |   |   |   |   |   |    |
      | 8  |   |   |   |   |   |   |   |   |   |    |
      | 9  |   |   |   |   |   |   |   |   |   |    |
      | 10 |   |   |   |   |   |   |   |   |   |    |
    When opponent launches
      | Location | 1,6 |
    Then result is
      | Miss |
    When opponent launches
      | Location | 1,7 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 1,8 |
    Then result is
      | Destroyed |
    Then my ships are now
      | Type       | Length | Status    | Location | Orientation |
      | Carrier    | 5      | Placed    | 1,1      | Horizontal  |
      | Battleship | 4      | Placed    | 2,1      | Horizontal  |
      | Cruiser    | 3      | Placed    | 3,1      | Horizontal  |
      | Submarine  | 3      | Placed    | 4,1      | Horizontal  |
      | Destroyer  | 2      | Destroyed | 1,7      | Horizontal  |
    When opponent launches
      | Location | 1,1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 1,2 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 1,3 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 1,4 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 1,5 |
    Then result is
      | Destroyed |
    Then my ships are now
      | Type       | Length | Status    | Location | Orientation |
      | Carrier    | 5      | Destroyed | 1,1      | Horizontal  |
      | Battleship | 4      | Placed    | 2,1      | Horizontal  |
      | Cruiser    | 3      | Placed    | 3,1      | Horizontal  |
      | Submarine  | 3      | Placed    | 4,1      | Horizontal  |
      | Destroyer  | 2      | Destroyed | 1,7      | Horizontal  |
    When opponent launches
      | Location | 2,1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 2,2 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 2,3 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 2,4 |
    Then result is
      | Destroyed |
    When opponent launches
      | Location | 3,1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 3,2 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 3,3 |
    Then result is
      | Destroyed |
    When opponent launches
      | Location | 4,1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 4,2 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 4,3 |
    Then result is
      | Destroyed |
    Then my ships are now
      | Type       | Length | Status    | Location | Orientation |
      | Carrier    | 5      | Destroyed | 1,1      | Horizontal  |
      | Battleship | 4      | Destroyed | 2,1      | Horizontal  |
      | Cruiser    | 3      | Destroyed | 3,1      | Horizontal  |
      | Submarine  | 3      | Destroyed | 4,1      | Horizontal  |
      | Destroyer  | 2      | Destroyed | 1,7      | Horizontal  |
    Then my ship display is now
      |    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
      | 1  | @ | @ | @ | @ | @ | X | @ | @ |   |    |
      | 2  | @ | @ | @ | @ |   |   |   |   |   |    |
      | 3  | @ | @ | @ |   |   |   |   |   |   |    |
      | 4  | @ | @ | @ |   |   |   |   |   |   |    |
      | 5  |   |   |   |   |   |   |   |   |   |    |
      | 6  |   |   |   |   |   |   |   |   |   |    |
      | 7  |   |   |   |   |   |   |   |   |   |    |
      | 8  |   |   |   |   |   |   |   |   |   |    |
      | 9  |   |   |   |   |   |   |   |   |   |    |
      | 10 |   |   |   |   |   |   |   |   |   |    |
    Then game is
      | Status | Winner |
      | Over   | I Lost |

  Scenario: Setup Ship Off Board
    Given ships are
      | Type    | Length | Status     | Location | Orientation |
      | Carrier | 5      | Not Placed |          |             |
    When placed
      | Ship        | Carrier    |
      | Location    | 1,7        |
      | Orientation | Horizontal |
    Then error is
      | Off board |
    When placed
      | Ship        | Carrier    |
      | Location    | 7,1        |
      | Orientation | Vertical   |
    Then error is
      | Off board |

  Scenario: Setup Ship Overlap
    Given my ships are
      | Type       | Length | Status     | Location | Orientation |
      | Battleship | 4      | Placed     | 3,3      | Vertical    |
      | Carrier    | 5      | Not Placed |          |             |
      | Cruiser    | 3      | Not Placed |          |             |
      | Submarine  | 3      | Not Placed |          |             |
      | Destroyer  | 2      | Not Placed |          |             |
    When placed
      | Ship        | Cruiser    |
      | Location    | 3,1        |
      | Orientation | Horizontal |
    Then error is
      | Overlap |
    When placed
      | Ship        | Cruiser    |
      | Location    | 4,3        |
      | Orientation | Horizontal |
    Then error is
      | Overlap |

  Scenario: Repeat Move
    Given my ships are
      | Type       | Length | Status | Location | Orientation |
      | Carrier    | 5      | Placed | 1,1      | Horizontal  |
      | Battleship | 4      | Placed | 2,1      | Horizontal  |
      | Cruiser    | 3      | Placed | 3,1      | Horizontal  |
      | Submarine  | 3      | Placed | 4,1      | Horizontal  |
      | Destroyer  | 2      | Placed | 1,7      | Horizontal  |
    When I launch
      | Location | 7,7 |
    When I launch
      | Location | 7,7 |
    Then error is
      | Duplicate launch |
