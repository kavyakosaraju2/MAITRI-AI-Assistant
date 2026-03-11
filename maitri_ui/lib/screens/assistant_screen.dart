import 'package:flutter/material.dart';
import '../widgets/chat_bubble.dart';

class AssistantScreen extends StatefulWidget {

  final List<Map<String, String>> messages;
  final Function(String) onCommand;

  const AssistantScreen({
    super.key,
    required this.messages,
    required this.onCommand
  });

  @override
  State<AssistantScreen> createState() => _AssistantScreenState();
}

class _AssistantScreenState extends State<AssistantScreen> {

  final ScrollController _scrollController = ScrollController();

  bool listening = false;

  @override
  void didUpdateWidget(covariant AssistantScreen oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (widget.messages.length != oldWidget.messages.length) {
      Future.delayed(const Duration(milliseconds: 100), () {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  void startListening() {

    setState(() {
      listening = true;
    });

    widget.onCommand("listen");

    Future.delayed(const Duration(seconds: 2), () {

      if (mounted) {
        setState(() {
          listening = false;
        });
      }

    });
  }

  @override
  Widget build(BuildContext context) {

    return Column(
      children: [

        Expanded(
          child: widget.messages.length == 1
              ? const Center(
                  child: Text(
                    "Ask MAITRI anything about your emails, tasks, or meetings.",
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 16,
                    ),
                  ),
                )
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: widget.messages.length,
                  itemBuilder: (context, index) {

                    final msg = widget.messages[index];

                    return ChatBubble(
                      text: msg["text"]!,
                      isUser: msg["role"] == "user",
                    );
                  },
                ),
        ),

        const SizedBox(height: 10),

        FloatingActionButton.extended(
          onPressed: startListening,
          icon: Icon(listening ? Icons.hearing : Icons.mic),
          label: Text(listening ? "Listening..." : "Speak"),
        ),

        const SizedBox(height: 20),

      ],
    );
  }
}