// Chapter Practice JavaScript

// Global variables
var currentQuestionIndex = 0;
var selectedAnswer = null;
var hasAnswered = false;
var questions = [];

// Initialize function that will be called from the template
function initChapterPractice(questionsData) {
    // In the template, Jinja2 sets the questionsData variable
    // The comment in the HTML template is replaced at runtime with actual data
    questions = questionsData || [];
    
    if (questions && questions.length > 0) {
        displayQuestion();
    }
    setupEventListeners();
}

function setupEventListeners() {
    const submitBtn = document.getElementById('submitBtn');
    const nextBtn = document.getElementById('nextBtn');
    const logoutBtn = document.getElementById('logoutBtnGlobal');

    if (submitBtn) {
        submitBtn.addEventListener('click', submitAnswer);
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', nextQuestion);
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

function displayQuestion() {
    if (currentQuestionIndex >= questions.length) {
        showCompletion();
        return;
    }

    const question = questions[currentQuestionIndex];
    selectedAnswer = null;
    hasAnswered = false;

    // Update UI
    document.getElementById('questionNumber').textContent = currentQuestionIndex + 1;
    document.getElementById('currentQuestionNum').textContent = currentQuestionIndex + 1;
    document.getElementById('questionText').textContent = question.question;

    // Display options
    const optionsContainer = document.getElementById('optionsContainer');
    optionsContainer.innerHTML = '';

    const sortedKeys = Object.keys(question.options).sort();
    
    sortedKeys.forEach(key => {
        const option = document.createElement('div');
        option.className = 'option-item';
        option.setAttribute('data-value', key);
        option.textContent = key + '. ' + question.options[key];
        option.addEventListener('click', () => selectOption(key));
        optionsContainer.appendChild(option);
    });

    // Reset feedback area
    document.getElementById('feedbackContainer').innerHTML = '';
    document.getElementById('submitBtn').style.display = 'inline-block';
    document.getElementById('nextBtn').style.display = 'none';
}

function selectOption(value) {
    if (hasAnswered) return;
    
    selectedAnswer = value;
    
    // Update UI
    document.querySelectorAll('.option-item').forEach(option => {
        option.classList.remove('selected');
    });
    
    document.querySelector(`[data-value="${value}"]`).classList.add('selected');
}

function submitAnswer() {
    if (!selectedAnswer || hasAnswered) {
        alert('请先选择一个答案');
        return;
    }
    
    hasAnswered = true;
    const question = questions[currentQuestionIndex];
    const isCorrect = selectedAnswer === question.answer;
    
    // Update UI
    document.querySelectorAll('.option-item').forEach(option => {
        const value = option.getAttribute('data-value');
        if (value === question.answer) {
            option.classList.add('correct');
        } else if (value === selectedAnswer && !isCorrect) {
            option.classList.add('incorrect');
        }
    });
    
    // Show feedback
    const feedbackContainer = document.getElementById('feedbackContainer');
    const feedback = document.createElement('div');
    feedback.className = isCorrect ? 'feedback-card feedback-correct' : 'feedback-card feedback-incorrect';
    feedback.textContent = isCorrect ? '✅ 答案正确！' : '❌ 答案错误！正确答案是 ' + question.answer;
    feedbackContainer.appendChild(feedback);
    
    // Record wrong answer if incorrect
    if (!isCorrect) {
        recordWrongAnswer(question);
    }
    
    // Update buttons
    document.getElementById('submitBtn').style.display = 'none';
    document.getElementById('nextBtn').style.display = 'inline-block';
}

function nextQuestion() {
    currentQuestionIndex++;
    displayQuestion();
}

function showCompletion() {
    const container = document.getElementById('questionContainer');
    container.innerHTML = `
        <div style="text-align: center; padding: 40px;">
            <h2>🎉 练习完成！</h2>
            <p>您已完成所有题目的练习</p>
            <div style="margin-top: 20px;">
                <a href="/chapter_practice" class="btn-primary">返回章节选择</a>
            </div>
        </div>
    `;
}

function recordWrongAnswer(question) {
    fetch('/api/record_wrong_answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question_id: question.id,
            question_text: question.question,
            question_type: question.type,
            correct_answer: question.answer,
            user_answer: selectedAnswer,
            question_options: JSON.stringify(question.options),
            source_doc: question.source_doc || ''
        })
    }).catch(error => {
        console.error('Error recording wrong answer:', error);
    });
}

async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        if (response.ok && result.redirect_url) {
            window.location.href = result.redirect_url;
        } else {
            alert(result.message || '登出失败');
        }
    } catch (error) {
        console.error('登出时出错:', error);
        alert('登出时出现错误');
    }
}
