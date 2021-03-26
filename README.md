# BBS and chatroom
### Use Network Programming to create a BBS system able to create boards, post, etc. And create a chatroom system within the BBS to privately/publicly chat with other people.

## How to run
#### server: 
  
  `python3 server.py port_number`

#### client: 
  
  `python3 client.py IP_addr port_number`

## Functions
### Part 1
1. Register with username, email and password.

   `register <username> <email> <password>`  
2. Login with username and password.

   `login <username> <password>`
3. Logout account.

   `logout`
4. Show username.

   `whoami`
5. List all users in BBS.

   `list-user`
6. Close connection.

   `exit`
   
### Part 2
1. Create a board.

   `create-board <name>`
2. Create a post.

   `create-post <board-name> --title <title> --content <content>`
3. List all boards in BBS.

   `list-board`
4. List all posts in a board named <board-name>.

   `list-post <board-name>`
5. Show the post which S/N is <post-S/N>.

   `read <post-S/N>`
6. Delete the post which S/N is <post-S/N>.

   `delete-post <post-S/N>`
7. Update the post which S/N is <post-S/N>.

   `update-post <post-S/N> --title/content <new>`
8. Leave a comment <comment> at the post which S/N is <post-S/N>.

   `comment <post-S/N> <comment>`
   
### Part 3
1. Create a chatroom which is named <username> in the client-side.

   `create-chatroom <port>`
2. List all Chatroom_ame, chatroom_status (open or close).

   `list-chatroom`
3. Join other chatroom server.

   `join-chatroom <chatroom_name>`
4. Attach the chatroom. (The instruction is for the chatroom owner)

   `attach`
5. Restart the chatroom, when the chatroom is closed.

   `restart-chatroom`
#### When In Chatroom
1. Leave chatroom.

   `leave-chatroom`
2. Detach the chatroom but do not close the chatroom. (The instruction is for the chatroom owner)

   `detach`
