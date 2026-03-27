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
      | Location | 2,3 |
    Then message sent
      | Player | Move | Result |
      | Ken    | 2,3  | Miss   |
    Then game is now
      | Status      | Current Turn |
      | In Progress | George       |
    When other player enters
      | Location | 4,5 |
    Then message sent
      | Player | Move | Result |
      | George | 4,5  | Miss   |
    Then game is now
      | Status      | Current Turn |
      | In Progress | Ken          |

  Scenario: End of game
    Given game is
      | Game ID    | Status      | Current Turn |
      | Ken-George | In Progress | George       |
    And my ships are all destroyed
      | Type       | Length | Location | Orientation |
      | Battleship | 4      | 1,1      | Vertical    |
      | Cruiser    | 3      | 2,2      | Horizontal  |
    Then game is now
      | Status | Winner |
      | Over   | George |
