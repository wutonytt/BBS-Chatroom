# BBS and chatroom
### Using Network Programming to create a BBS system able to create boards, post, etc. And create a chatroom system within the BBS to privately/publicly chat with other people.

## How to run
Run the server first, and then run the clients. (Up to 10 clients)
#### server: 
  
  `python3 server.py port_number`

#### client: 
  
  `python3 client.py IP_addr port_number`

## Functions
### Part 1: User Information
* Register with username, email and password.

   `register <username> <email> <password>`  
* Login with username and password.

   `login <username> <password>`
* Logout account.

   `logout`
* Show username.

   `whoami`
* List all users in BBS.

   `list-user`
* Close connection.

   `exit`
   
### Part 2: Boards and Posts
* Create a board.

   `create-board <name>`
* Create a post.

   `create-post <board-name> --title <title> --content <content>`
* List all boards in BBS.

   `list-board`
* List all posts in a board named <board-name>.

   `list-post <board-name>`
* Show the post which S/N is <post-S/N>.

   `read <post-S/N>`
* Delete the post which S/N is <post-S/N>.

   `delete-post <post-S/N>`
* Update the post which S/N is <post-S/N>.

   `update-post <post-S/N> --title/content <new>`
* Leave a comment <comment> at the post which S/N is <post-S/N>.

   `comment <post-S/N> <comment>`
   
### Part 3: Chatrooms
* Create a chatroom which is named <username> in the client-side.

   `create-chatroom <port>`
* List all Chatroom_ame, chatroom_status (open or close).

   `list-chatroom`
* Join other chatroom server.

   `join-chatroom <chatroom_name>`
* Attach the chatroom. (The instruction is for the chatroom owner)

   `attach`
* Restart the chatroom, when the chatroom is closed.

   `restart-chatroom`
   #### When In Chatroom
   * Leave chatroom.

      `leave-chatroom`
   * Detach the chatroom but do not close the chatroom. (The instruction is for the chatroom owner)

      `detach`
