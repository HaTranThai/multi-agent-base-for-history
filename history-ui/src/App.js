import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

// Component để format text đẹp hơn
const FormattedText = ({ text }) => {
  // Format text thông thường
  const formatLines = (lines) => {
    return lines.map((line, i) => {
      // Bold cho tiêu đề (dòng có ** hoặc bắt đầu bằng số)
      if (line.includes('**')) {
        const parts = line.split('**');
        return (
          <p key={i} style={{ margin: '8px 0' }}>
            {parts.map((part, j) => 
              j % 2 === 1 ? <strong key={j}>{part}</strong> : part
            )}
          </p>
        );
      }
      // Bullet points
      if (line.trim().startsWith('*') || line.trim().startsWith('-')) {
        return (
          <li key={i} style={{ marginLeft: '20px', marginBottom: '4px' }}>
            {line.replace(/^[*-]\s*/, '')}
          </li>
        );
      }
      // Paragraph thông thường
      if (line.trim()) {
        return <p key={i} style={{ margin: '8px 0' }}>{line}</p>;
      }
      return <br key={i} />;
    });
  };

  // Kiểm tra nếu có bảng (table markdown format)
  const hasTable = text.includes('|') && text.split('\n').filter(line => line.includes('|')).length >= 3;

  if (hasTable) {
    const lines = text.split('\n');
    const tableLines = [];
    const otherLines = [];
    let inTable = false;

    lines.forEach(line => {
      if (line.includes('|')) {
        inTable = true;
        tableLines.push(line);
      } else if (inTable && !line.trim()) {
        inTable = false;
      } else if (inTable) {
        tableLines.push(line);
      } else {
        otherLines.push(line);
      }
    });

    if (tableLines.length >= 3) {
      // Parse table
      const rows = tableLines
        .filter(line => line.trim() && !line.includes('---'))
        .map(line => 
          line.split('|')
            .map(cell => cell.trim())
            .filter(cell => cell)
        );

      const [headers, ...bodyRows] = rows;

      return (
        <div>
          {otherLines.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              {formatLines(otherLines)}
            </div>
          )}
          <div style={{ overflowX: 'auto', margin: '12px 0' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '14px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              borderRadius: '8px',
              overflow: 'hidden'
            }}>
              <thead>
                <tr style={{ background: '#1a1a1a', color: 'white' }}>
                  {headers.map((header, i) => (
                    <th key={i} style={{
                      padding: '12px 10px',
                      textAlign: 'left',
                      fontWeight: '600',
                      borderRight: i < headers.length - 1 ? '1px solid rgba(255,255,255,0.1)' : 'none'
                    }}>
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bodyRows.map((row, i) => (
                  <tr key={i} style={{
                    background: i % 2 === 0 ? '#f8f8f8' : 'white',
                    transition: 'background 0.2s'
                  }}>
                    {row.map((cell, j) => (
                      <td key={j} style={{
                        padding: '10px',
                        borderRight: j < row.length - 1 ? '1px solid #e0e0e0' : 'none',
                        borderBottom: i < bodyRows.length - 1 ? '1px solid #e0e0e0' : 'none',
                        lineHeight: '1.6',
                        verticalAlign: 'top'
                      }}>
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }
  }

  return <div>{formatLines(text.split('\n'))}</div>;
};

function App() {
  const [messages, setMessages] = useState([]); // lịch sử chat
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [streamingText, setStreamingText] = useState(""); // Text đang stream
  const [isStreaming, setIsStreaming] = useState(false); // Đang stream hay không

  // Tạo hoặc lấy session_id khi component mount
  useEffect(() => {
    let sid = localStorage.getItem("history_session_id");
    if (!sid) {
      sid = "session_" + Date.now();
      localStorage.setItem("history_session_id", sid);
    }
    setSessionId(sid);
  }, []);

  const clearChat = () => {
    setMessages([]);
    const newSid = "session_" + Date.now();
    localStorage.setItem("history_session_id", newSid);
    setSessionId(newSid);
  };

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    const question = input;
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/history-qa", {
        session_id: sessionId,
        question: question,
      });

      // Bắt đầu streaming effect
      const fullText = res.data.answer;
      setLoading(false);
      setIsStreaming(true);
      setStreamingText("");

      // Thêm placeholder message để render streaming
      const botMsgIndex = messages.length + 1;
      setMessages((prev) => [...prev, { sender: "bot", text: "", isStreaming: true }]);

      // Stream từng ký tự
      let currentIndex = 0;
      const streamInterval = setInterval(() => {
        if (currentIndex < fullText.length) {
          const chunkSize = Math.floor(Math.random() * 3) + 1; // 1-3 ký tự mỗi lần
          const nextChunk = fullText.slice(currentIndex, currentIndex + chunkSize);
          currentIndex += chunkSize;
          
          setStreamingText((prev) => prev + nextChunk);
          
          // Update message cuối cùng
          setMessages((prev) => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              sender: "bot",
              text: fullText.slice(0, currentIndex),
              isStreaming: true
            };
            return newMessages;
          });
        } else {
          clearInterval(streamInterval);
          setIsStreaming(false);
          setStreamingText("");
          
          // Finalize message
          setMessages((prev) => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              sender: "bot",
              text: fullText,
              isStreaming: false
            };
            return newMessages;
          });
        }
      }, 20); // 20ms mỗi lần update (nhanh và mượt)

    } catch (e) {
      console.error("API Error:", e);
      setLoading(false);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Lỗi kết nối API!" },
      ]);
    }
  };

  return (
    <div className="background">
      <div className="chat-window">

        <div className="header">
          <h2 className="header-title">📚 Lịch sử AI</h2>
          <button className="clear-btn" onClick={clearChat} title="Bắt đầu cuộc trò chuyện mới">
            🗑️ Xóa
          </button>
        </div>

        <div className="chat-area">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`bubble ${msg.sender === "user" ? "user" : "bot"}`}
            >
              {msg.sender === "bot" ? (
                <>
                  <FormattedText text={msg.text} />
                  {msg.isStreaming && <span className="streaming-cursor">▋</span>}
                </>
              ) : (
                msg.text
              )}
            </div>
          ))}

          {loading && (
            <div className="bubble bot typing">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          )}
        </div>

        <div className="input-area">
          <input
            className="text-input"
            placeholder="Nhập câu hỏi..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />

          <button className="send-btn" onClick={sendMessage}>
            Gửi
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
