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
      | Location    | A1         |
      | Orientation | Horizontal |
    Then my ships are now
      | Type       | Length | Status     | Location | Orientation |
      | Carrier    | 5      | Placed     | A1       | Horizontal  |
      | Battleship | 4      | Not Placed |          |             |
      | Cruiser    | 3      | Not Placed |          |             |
      | Submarine  | 3      | Not Placed |          |             |
      | Destroyer  | 2      | Not Placed |          |             |
    When placed
      | Ship        | Battleship |
      | Location    | A2         |
      | Orientation | Horizontal |
    When placed
      | Ship        | Cruiser    |
      | Location    | A3         |
      | Orientation | Horizontal |
    When placed
      | Ship        | Submarine  |
      | Location    | A4         |
      | Orientation | Horizontal |
    When placed
      | Ship        | Destroyer  |
      | Location    | G1         |
      | Orientation | Horizontal |
    Then my ships are now
      | Type       | Length | Status | Location | Orientation |
      | Carrier    | 5      | Placed | A1       | Horizontal  |
      | Battleship | 4      | Placed | A2       | Horizontal  |
      | Cruiser    | 3      | Placed | A3       | Horizontal  |
      | Submarine  | 3      | Placed | A4       | Horizontal  |
      | Destroyer  | 2      | Placed | G1       | Horizontal  |
    Then my ship display is now
      |   | A | B | C | D | E | F | G | H | I | J |
      | 1 | A | A | A | A | A |   | D | D |   |   |
      | 2 | B | B | B | B |   |   |   |   |   |   |
      | 3 | C | C | C |   |   |   |   |   |   |   |
      | 4 | S | S | S |   |   |   |   |   |   |   |
      | 5 |   |   |   |   |   |   |   |   |   |   |
      | 6 |   |   |   |   |   |   |   |   |   |   |
      | 7 |   |   |   |   |   |   |   |   |   |   |
      | 8 |   |   |   |   |   |   |   |   |   |   |
      | 9 |   |   |   |   |   |   |   |   |   |   |
      | 10|   |   |   |   |   |   |   |   |   |   |
    Then game is
      | Status        | Winner |
      | Ready to Play | TBD    |

  Scenario: Some hits and misses
    Given my ships are
      | Type       | Length | Status | Location | Orientation |
      | Carrier    | 5      | Placed | A1       | Horizontal  |
      | Battleship | 4      | Placed | A2       | Horizontal  |
      | Cruiser    | 3      | Placed | A3       | Horizontal  |
      | Submarine  | 3      | Placed | A4       | Horizontal  |
      | Destroyer  | 2      | Placed | G1       | Horizontal  |
    Given my ship display is
      |   | A | B | C | D | E | F | G | H | I | J |
      | 1 | A | A | A | A | A |   | D | D |   |   |
      | 2 | B | B | B | B |   |   |   |   |   |   |
      | 3 | C | C | C |   |   |   |   |   |   |   |
      | 4 | S | S | S |   |   |   |   |   |   |   |
      | 5 |   |   |   |   |   |   |   |   |   |   |
      | 6 |   |   |   |   |   |   |   |   |   |   |
      | 7 |   |   |   |   |   |   |   |   |   |   |
      | 8 |   |   |   |   |   |   |   |   |   |   |
      | 9 |   |   |   |   |   |   |   |   |   |   |
      | 10|   |   |   |   |   |   |   |   |   |   |
    When opponent launches
      | Location | F1 |
    Then result is
      | Miss |
    When opponent launches
      | Location | G1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | H1 |
    Then result is
      | Destroyer Destroyed |
    Then my ships are now
      | Type       | Length | Status    | Location | Orientation |
      | Carrier    | 5      | Placed    | A1       | Horizontal  |
      | Battleship | 4      | Placed    | A2       | Horizontal  |
      | Cruiser    | 3      | Placed    | A3       | Horizontal  |
      | Submarine  | 3      | Placed    | A4       | Horizontal  |
      | Destroyer  | 2      | Destroyed | G1       | Horizontal  |
    When opponent launches
      | Location | A1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | B1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | C1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | D1 |
    Then result is
      | Hit |
    When opponent launches
      | Location | E1 |
    Then result is
      | Carrier Destroyed |
    Then my ships are now
      | Type       | Length | Status    | Location | Orientation |
      | Carrier    | 5      | Destroyed | A1       | Horizontal  |
      | Battleship | 4      | Placed    | A2       | Horizontal  |
      | Cruiser    | 3      | Placed    | A3       | Horizontal  |
      | Submarine  | 3      | Placed    | A4       | Horizontal  |
      | Destroyer  | 2      | Destroyed | G1       | Horizontal  |
    When opponent launches
      | Location | A2 |
    Then result is
      | Hit |
    When opponent launches
      | Location | B2 |
    Then result is
      | Hit |
    When opponent launches
      | Location | C2 |
    Then result is
      | Hit |
    When opponent launches
      | Location | D2 |
    Then result is
      | Battleship Destroyed |
    When opponent launches
      | Location | A3 |
    Then result is
      | Hit |
    When opponent launches
      | Location | B3 |
    Then result is
      | Hit |
    When opponent launches
      | Location | C3 |
    Then result is
      | Cruiser Destroyed |
    When opponent launches
      | Location | A4 |
    Then result is
      | Hit |
    When opponent launches
      | Location | B4 |
    Then result is
      | Hit |
    When opponent launches
      | Location | C4 |
    Then result is
      | Submarine Destroyed |
    Then my ships are now
      | Type       | Length | Status    | Location | Orientation |
      | Carrier    | 5      | Destroyed | A1       | Horizontal  |
      | Battleship | 4      | Destroyed | A2       | Horizontal  |
      | Cruiser    | 3      | Destroyed | A3       | Horizontal  |
      | Submarine  | 3      | Destroyed | A4       | Horizontal  |
      | Destroyer  | 2      | Destroyed | G1       | Horizontal  |
    Then my ship display is now
      |   | A | B | C | D | E | F | G | H | I | J |
      | 1 | @ | @ | @ | @ | @ | X | @ | @ |   |   |
      | 2 | @ | @ | @ | @ |   |   |   |   |   |   |
      | 3 | @ | @ | @ |   |   |   |   |   |   |   |
      | 4 | @ | @ | @ |   |   |   |   |   |   |   |
      | 5 |   |   |   |   |   |   |   |   |   |   |
      | 6 |   |   |   |   |   |   |   |   |   |   |
      | 7 |   |   |   |   |   |   |   |   |   |   |
      | 8 |   |   |   |   |   |   |   |   |   |   |
      | 9 |   |   |   |   |   |   |   |   |   |   |
      | 10|   |   |   |   |   |   |   |   |   |   |
    Then game is
      | Status | Winner |
      | Over   | I Lost |

  Scenario: Setup Ship Off Board
    Given ships are
      | Type    | Length | Status     | Location | Orientation |
      | Carrier | 5      | Not Placed |          |             |
    When placed
      | Ship        | Carrier    |
      | Location    | G1         |
      | Orientation | Horizontal |
    Then error is
      | Off board |
    When placed
      | Ship        | Carrier  |
      | Location    | A7       |
      | Orientation | Vertical |
    Then error is
      | Off board |

  Scenario: Setup Ship Overlap
    Given my ships are
      | Type       | Length | Status     | Location | Orientation |
      | Battleship | 4      | Placed     | C3       | Vertical    |
      | Carrier    | 5      | Not Placed |          |             |
      | Cruiser    | 3      | Not Placed |          |             |
      | Submarine  | 3      | Not Placed |          |             |
      | Destroyer  | 2      | Not Placed |          |             |
    When placed
      | Ship        | Cruiser    |
      | Location    | A3         |
      | Orientation | Horizontal |
    Then error is
      | Overlap |
    When placed
      | Ship        | Cruiser    |
      | Location    | C4         |
      | Orientation | Horizontal |
    Then error is
      | Overlap |

  Scenario: Repeat Move
    Given my ships are
      | Type       | Length | Status | Location | Orientation |
      | Carrier    | 5      | Placed | A1       | Horizontal  |
      | Battleship | 4      | Placed | A2       | Horizontal  |
      | Cruiser    | 3      | Placed | A3       | Horizontal  |
      | Submarine  | 3      | Placed | A4       | Horizontal  |
      | Destroyer  | 2      | Placed | G1       | Horizontal  |
    When I launch
      | Location | G7 |
    When I launch
      | Location | G7 |
    Then error is
      | Duplicate launch |
