Feature: Board Game Protocol

  Scenario: Start Game
    Given I am
      | Ken |
    And game does not exist
      | Game ID    |
      | Ken-George |
    When player enters
      | My Name   | Ken    |
      | Your Name | George |
    Then game is now
      | Game ID    | Status      | Current Turn |
      | Ken-George | In Progress | Ken          |

  Scenario: Send a move
    Given game is
      | Game ID    | Status      | Current Turn |
      | Ken-George | In Progress | Ken          |
    When player enters
      | Location | C2 |
    Then message sent
      | Player | Move | Result |
      | Ken    | C2   | Miss   |
    Then game is now
      | Status      | Current Turn |
      | In Progress | George       |
    When other player enters
      | Location | E4 |
    Then message sent
      | Player | Move | Result |
      | George | E4   | Miss   |
    Then game is now
      | Status      | Current Turn |
      | In Progress | Ken          |

  Scenario: End of game
    Given game is
      | Game ID    | Status      | Current Turn |
      | Ken-George | In Progress | George       |
    And my ships are all destroyed
      | Type       | Length | Location | Orientation |
      | Carrier    | 5      | A1       | Horizontal  |
      | Battleship | 4      | A2       | Horizontal  |
      | Cruiser    | 3      | A3       | Horizontal  |
      | Submarine  | 3      | A4       | Horizontal  |
      | Destroyer  | 2      | G1       | Horizontal  |
    Then game is now
      | Status | Winner |
      | Over   | George |
