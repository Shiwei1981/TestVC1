async function doDivine() {
    const question = document.getElementById("question").value.trim();
    const birthInfo = document.getElementById("birth_info").value.trim();
    const btn = document.getElementById("btn-divine");
    const resultBox = document.getElementById("result");
    const resultText = document.getElementById("result-text");

    if (!question) {
        alert("请输入您的问题！");
        return;
    }

    btn.disabled = true;
    btn.textContent = "占卜中…";
    resultBox.style.display = "block";
    resultText.textContent = "正在为您推演天机，请稍候…";

    try {
        const resp = await fetch("/divine", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question, birth_info: birthInfo }),
        });
        const data = await resp.json();
        if (!resp.ok) {
            resultText.textContent = data.error || "请求失败，请稍后重试。";
            return;
        }
        resultText.textContent = data.answer;

        // Prepend to history list
        const list = document.getElementById("history-list");
        const emptyHint = document.getElementById("empty-hint");
        if (emptyHint) emptyHint.remove();

        if (!list) {
            // Create list container if not present
            const section = document.querySelector(".history-section");
            const newList = document.createElement("div");
            newList.className = "history-list";
            newList.id = "history-list";
            section.appendChild(newList);
            prependItem(newList, question, data.answer, data.created_at);
        } else {
            prependItem(list, question, data.answer, data.created_at);
        }
    } catch (e) {
        resultText.textContent = "网络错误，请检查连接后重试。";
    } finally {
        btn.disabled = false;
        btn.textContent = "起卦";
    }
}

function prependItem(list, question, answer, time) {
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML =
        `<div class="history-meta">${time}</div>` +
        `<div class="history-q"><strong>问：</strong>${escapeHtml(question)}</div>` +
        `<div class="history-a"><strong>答：</strong>${escapeHtml(answer)}</div>`;
    list.prepend(div);
}

function escapeHtml(text) {
    const d = document.createElement("div");
    d.textContent = text;
    return d.innerHTML;
}
