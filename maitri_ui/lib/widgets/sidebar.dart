import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class Sidebar extends StatefulWidget {

  final String selectedPage;
  final Function(String) onSelect;

  final List chats;
  final Function(dynamic) onOpenChat;
  final Function refreshChats;

  const Sidebar({
    super.key,
    required this.selectedPage,
    required this.onSelect,
    required this.chats,
    required this.onOpenChat,
    required this.refreshChats
  });

  @override
  State<Sidebar> createState() => _SidebarState();
}

class _SidebarState extends State<Sidebar> {
  Widget buildItem(String name, IconData icon) {

    return ListTile(
      leading: Icon(icon),
      title: Text(name),
      selected: widget.selectedPage == name,
      onTap: () => widget.onSelect(name),
    );
  }

  Future<void> deleteChat(String chatId) async {

    await http.delete(
      Uri.parse("http://localhost:8000/delete_chat/$chatId"),
    );
    
    widget.refreshChats();
  }

  @override
  Widget build(BuildContext context) {

    return Container(
      width: 230,
      color: const Color(0xFF1E1E1E),

      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,

        children: [

          const SizedBox(height: 30),

          Center(
            child: Column(
              children: [

                ClipOval(
                  child: Image.asset(
                    "assets/logo.png",
                    width: 90,
                  ),
                ),

                const SizedBox(height: 10),

                const Text(
                  "MAITRI",
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold
                  ),
                ),

              ],
            ),
          ),

          const SizedBox(height: 25),

          const Padding(
            padding: EdgeInsets.all(12),
            child: Text(
              "Chats",
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold
              ),
            ),
          ),

          Expanded(
            child: ListView(
              children: [

                // NEW CHAT BUTTON
                ListTile(
                  leading: const Icon(Icons.add),
                  title: const Text("New Chat"),
                  onTap: () {

                    widget.onOpenChat({
                      "id": null,
                      "title": "New Chat",
                      "messages": [
                        {"role":"assistant","text":"Hello! I am MAITRI."}
                      ]
                    });

                  },
                ),

                for (var chat in widget.chats)

                  if (chat["title"] != null && chat["title"] != "")

                    ListTile(
                      leading: const Icon(Icons.chat),

                      title: Text(
                        chat["title"] ?? "Chat",
                        overflow: TextOverflow.ellipsis,
                      ),

                      onTap: () {
                        widget.onOpenChat(chat);
                      },

                      trailing: IconButton(
                        icon: const Icon(Icons.delete, size: 18),
                        onPressed: () {
                          deleteChat(chat["id"]);
                        },
                      ),
                    ),

              ],
            ),
          ),

          const Divider(),

          buildItem("dashboard", Icons.dashboard),
          buildItem("assistant", Icons.smart_toy),
          buildItem("emails", Icons.email),
          buildItem("calendar", Icons.calendar_month),
          buildItem("tasks", Icons.check_circle),

        ],
      ),
    );
  }
}