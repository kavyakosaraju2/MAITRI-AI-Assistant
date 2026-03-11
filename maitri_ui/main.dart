import 'package:flutter/material.dart';
import 'widgets/sidebar.dart';
import 'screens/assistant_screen.dart';
import 'screens/emails_screen.dart';
import 'screens/calendar_screen.dart';
import 'screens/tasks_screen.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_tts/flutter_tts.dart';
import 'screens/dashboard_screen.dart';

void main() {
runApp(const MaitriApp());
}

class MaitriApp extends StatelessWidget {
const MaitriApp({super.key});

@override
Widget build(BuildContext context) {
return MaterialApp(
title: 'MAITRI',
debugShowCheckedModeBanner: false,
theme: ThemeData.dark(),
home: const MaitriHome(),
);
}
}

class MaitriHome extends StatefulWidget {
const MaitriHome({super.key});

@override
State<MaitriHome> createState() => _MaitriHomeState();
}

class _MaitriHomeState extends State<MaitriHome> {

String selectedPage = "assistant";

FlutterTts tts = FlutterTts();

List<Map<String,String>> messages = [
{"role":"assistant","text":"Hello! I am MAITRI."}
];

List<dynamic> chatHistory = [];

String currentChatTitle = "New Chat";
String? currentChatId;

@override
void initState() {
super.initState();
loadChats();
}

Future<void> sendCommand(String command) async {

final url = Uri.parse("http://127.0.0.1:8000/command");

final response = await http.post(
  url,
  headers: {"Content-Type": "application/json"},
  body: jsonEncode({"command": command}),
);

final data = jsonDecode(response.body);

if (currentChatTitle == "New Chat") {
  currentChatTitle = data["command"];
}

setState(() {

  messages.add({
    "role": "user",
    "text": data["command"]
  });

  messages.add({
    "role": "assistant",
    "text": data["response"]
  });

});

await tts.speak(data["response"]);

await saveChat();
await loadChats();

}

Future<void> loadChats() async {

final url = Uri.parse("http://localhost:8000/chats");

final response = await http.get(url);

final data = jsonDecode(response.body);

setState(() {
  chatHistory = data;
});

}

Future<void> saveChat() async {

final url = Uri.parse("http://localhost:8000/save_chat");

final response = await http.post(
  url,
  headers: {"Content-Type": "application/json"},
  body: jsonEncode({
    "title": currentChatTitle,
    "messages": messages,
    "chat_id": currentChatId
  }),
);

final data = jsonDecode(response.body);

if (data["chat_id"] != null) {
  currentChatId = data["chat_id"];
}

}

Widget buildPage(){

switch(selectedPage){

  case "dashboard":
    return DashboardScreen(
      onNavigate: (page){
        setState(() {
          selectedPage = page;
        });
      },
    );

  case "emails":
    return const EmailScreen();

  case "calendar":
    return const CalendarScreen();

  case "tasks":
    return const TasksScreen();

  default:
    return AssistantScreen(
      messages: messages,
      onCommand: sendCommand,
    );
}

}

@override
Widget build(BuildContext context){

return Scaffold(
  backgroundColor: const Color(0xFF121212),

  body: Row(
    children: [

      Sidebar(
        selectedPage: selectedPage,
        chats: chatHistory,
        refreshChats: loadChats,
        onOpenChat: (chat){

          setState(() {

            messages = (chat["messages"] as List)
                .map((m) => {
                      "role": m["role"].toString(),
                      "text": m["text"].toString()
                    })
                .toList();

            currentChatTitle = chat["title"] ?? "Chat";
            currentChatId = chat["id"];
            selectedPage = "assistant";

          });

        },
        onSelect: (page){

          setState(() {
            selectedPage = page;
          });

        },
      ),

      Expanded(child: buildPage())

    ],
  ),
);

}
}