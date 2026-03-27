Feature: Game

  Scenario: Setup Ship Happy Path
    Given my ships are
      | Type       | Length | Status     | Location | Orientation |
      | Battleship | 4      | Not Placed |          |             |
      | Cruiser    | 3      | Not Placed |          |             |
    When placed
      | Ship        | Battleship |
      | Location    | 1,1        |
      | Orientation | Vertical   |
    Then my ships are now
      | Type       | Length | Status     | Location | Orientation |
      | Battleship | 4      | Placed     | 1,1      | Vertical    |
      | Cruiser    | 3      | Not Placed |          |             |
    When placed
      | Ship        | Cruiser    |
      | Location    | 2,2        |
      | Orientation | Horizontal |
    Then my ships are now
      | Type       | Length | Status | Location | Orientation |
      | Battleship | 4      | Placed | 1,1      | Vertical    |
      | Cruiser    | 3      | Placed | 2,2      | Horizontal  |
    Then my ship display is now
      |    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
      | 1  | B |   |   |   |   |   |   |   |   |    |
      | 2  | B | C | C | C |   |   |   |   |   |    |
      | 3  | B |   |   |   |   |   |   |   |   |    |
      | 4  | B |   |   |   |   |   |   |   |   |    |
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
      | Battleship | 4      | Placed | 1,1      | Vertical    |
      | Cruiser    | 3      | Placed | 2,2      | Horizontal  |
    Given my ship display is
      |    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
      | 1  | B |   |   |   |   |   |   |   |   |    |
      | 2  | B | C | C | C |   |   |   |   |   |    |
      | 3  | B |   |   |   |   |   |   |   |   |    |
      | 4  | B |   |   |   |   |   |   |   |   |    |
      | 5  |   |   |   |   |   |   |   |   |   |    |
      | 6  |   |   |   |   |   |   |   |   |   |    |
      | 7  |   |   |   |   |   |   |   |   |   |    |
      | 8  |   |   |   |   |   |   |   |   |   |    |
      | 9  |   |   |   |   |   |   |   |   |   |    |
      | 10 |   |   |   |   |   |   |   |   |   |    |
    When opponent launches
      | Location | 1,2 |
    Then result is
      | Miss |
    Then my ship display is now
      |    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
      | 1  | B | X |   |   |   |   |   |   |   |    |
      | 2  | B | C | C | C |   |   |   |   |   |    |
      | 3  | B |   |   |   |   |   |   |   |   |    |
      | 4  | B |   |   |   |   |   |   |   |   |    |
      | 5  |   |   |   |   |   |   |   |   |   |    |
      | 6  |   |   |   |   |   |   |   |   |   |    |
      | 7  |   |   |   |   |   |   |   |   |   |    |
      | 8  |   |   |   |   |   |   |   |   |   |    |
      | 9  |   |   |   |   |   |   |   |   |   |    |
      | 10 |   |   |   |   |   |   |   |   |   |    |
    When opponent launches
      | Location | 1,1 |
    Then result is
      | Hit |
    Then my ship display is now
      |    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
      | 1  | @ | X |   |   |   |   |   |   |   |    |
      | 2  | B | C | C | C |   |   |   |   |   |    |
      | 3  | B |   |   |   |   |   |   |   |   |    |
      | 4  | B |   |   |   |   |   |   |   |   |    |
      | 5  |   |   |   |   |   |   |   |   |   |    |
      | 6  |   |   |   |   |   |   |   |   |   |    |
      | 7  |   |   |   |   |   |   |   |   |   |    |
      | 8  |   |   |   |   |   |   |   |   |   |    |
      | 9  |   |   |   |   |   |   |   |   |   |    |
      | 10 |   |   |   |   |   |   |   |   |   |    |
    Then my ships are now
      | Type       | Length | Status | Location | Orientation |
      | Battleship | 4      | Hit    | 1,1      | Vertical    |
      | Cruiser    | 3      | Placed | 2,2      | Horizontal  |
    When opponent launches
      | Location | 2,1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 3,1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | 4,1 |
    Then result is
      | Destroyed |
    Then my ship display is now
      |    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
      | 1  | @ | X |   |   |   |   |   |   |   |    |
      | 2  | @ | C | C | C |   |   |   |   |   |    |
      | 3  | @ |   |   |   |   |   |   |   |   |    |
      | 4  | @ |   |   |   |   |   |   |   |   |    |
      | 5  |   |   |   |   |   |   |   |   |   |    |
      | 6  |   |   |   |   |   |   |   |   |   |    |
      | 7  |   |   |   |   |   |   |   |   |   |    |
      | 8  |   |   |   |   |   |   |   |   |   |    |
      | 9  |   |   |   |   |   |   |   |   |   |    |
      | 10 |   |   |   |   |   |   |   |   |   |    |
    Then my ships are now
      | Type       | Length | Status    | Location | Orientation |
      | Battleship | 4      | Destroyed | 1,1      | Vertical    |
      | Cruiser    | 3      | Placed    | 2,2      | Horizontal  |
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
    Then my ships are now
      | Type       | Length | Status    | Location | Orientation |
      | Battleship | 4      | Destroyed | 1,1      | Vertical    |
      | Cruiser    | 3      | Destroyed | 2,2      | Horizontal  |
    Then game is
      | Status | Winner |
      | Over   | I Lost |

  Scenario: Setup Ship Off Board
    Given ships are
      | Type       | Length | Status     | Location | Orientation |
      | Battleship | 4      | Not Placed |          |             |
    When placed
      | Ship        | Battleship |
      | Location    | 1,8        |
      | Orientation | Horizontal |
    Then error is
      | Off board |
    When placed
      | Ship        | Battleship |
      | Location    | 8,1        |
      | Orientation | Vertical   |
    Then error is
      | Off board |

  Scenario: Setup Ship Overlap
    Given my ships are
      | Type       | Length | Status     | Location | Orientation |
      | Battleship | 4      | Placed     | 3,3      | Vertical    |
      | Cruiser    | 3      | Not Placed |          |             |
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
      | Battleship | 4      | Placed | 1,1      | Vertical    |
      | Cruiser    | 3      | Placed | 2,2      | Horizontal  |
    When I launch
      | Location | 2,2 |
    When I launch
      | Location | 2,2 |
    Then error is
      | Duplicate launch |
