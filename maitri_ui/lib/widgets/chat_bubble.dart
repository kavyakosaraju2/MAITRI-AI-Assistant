import 'package:flutter/material.dart';

class ChatBubble extends StatelessWidget {

  final String text;
  final bool isUser;

  const ChatBubble({
    super.key,
    required this.text,
    required this.isUser
  });

  @override
  Widget build(BuildContext context) {

    return Align(
      alignment:
          isUser ? Alignment.centerRight : Alignment.centerLeft,

      child: Container(
        margin: const EdgeInsets.symmetric(
            vertical: 6,
            horizontal: 10),

        padding: const EdgeInsets.all(14),

        decoration: BoxDecoration(
          
          gradient: isUser
              ? const LinearGradient(
                  colors: [
                  Color(0xFF4A90E2),
                  Color(0xFF357ABD)
                ],
              )
            : const LinearGradient(
                colors: [
                Color(0xFF2E2E2E),
                Color(0xFF1E1E1E)
              ],
            ),

          borderRadius: BorderRadius.circular(14),
        ),

        child: Text(
          text,
          style: const TextStyle(fontSize: 16),
        ),
      ),
    );
  }
}