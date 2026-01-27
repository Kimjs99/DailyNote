// Supabase 설정
const SUPABASE_URL = 'https://zbhhjoghntjzdyfttmuo.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpiaGhqb2dobnRqemR5ZnR0bXVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUwOTcwMDgsImV4cCI6MjA4MDY3MzAwOH0.JQsocWDhTrVMITyTBX4xFg6vToyS6PHQ8lYCgv5EETI';

// Supabase 클라이언트 초기화
let supabaseClient = null;
if (SUPABASE_URL !== 'YOUR_SUPABASE_URL' && SUPABASE_ANON_KEY !== 'YOUR_SUPABASE_ANON_KEY') {
    supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
}

// 게임 상태
let gameState = {
    cards: [],
    flippedCards: [],
    matchedPairs: 0,
    attempts: 0,
    startTime: null,
    timerInterval: null,
    isProcessing: false,
    difficulty: 'medium'
};

// 카드 이미지 세트
const cardImageSets = {
    fruits: ['🍎', '🍌', '🍇', '🍊', '🍓', '🍑', '🥝', '🍉', '🍒', '🥭', '🍍', '🍋', '🍐', '🥑', '🫐', '🍈'],
    shapes: ['🔴', '🔵', '🟢', '🟡', '🟠', '🟣', '⚫', '⚪', '🔶', '🔷', '🔸', '🔹', '🟥', '🟦', '🟩', '🟨'],
    sports: ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🥊', '🏹', '⛳', '🏌️', '🏄', '🏊'],
    signs: ['🚦', '🚸', '⛔', '🚫', '🚭', '🚯', '🚱', '🚳', '🚷', '🚺', '🚻', '🚼', '🚾', '🛂', '🛃', '🛄']
};

// 현재 카드 이미지 세트
let currentCardImages = cardImageSets.fruits;

// 난이도 설정
const difficultyConfig = {
    easy: { rows: 2, cols: 4, pairs: 4 },
    medium: { rows: 3, cols: 4, pairs: 6 },
    hard: { rows: 4, cols: 4, pairs: 8 }
};

// DOM 요소
const gameBoard = document.getElementById('gameBoard');
const attemptsDisplay = document.getElementById('attempts');
const timerDisplay = document.getElementById('timer');
const difficultySelect = document.getElementById('difficulty');
const cardThemeSelect = document.getElementById('cardTheme');
const newGameBtn = document.getElementById('newGameBtn');
const leaderboardBtn = document.getElementById('leaderboardBtn');
const gameCompleteModal = document.getElementById('gameCompleteModal');
const leaderboardModal = document.getElementById('leaderboardModal');
const playerNameInput = document.getElementById('playerName');
const saveScoreBtn = document.getElementById('saveScoreBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const closeLeaderboardBtn = document.getElementById('closeLeaderboardBtn');

// 게임 초기화
function initGame() {
    const config = difficultyConfig[gameState.difficulty];
    gameState.cards = [];
    gameState.flippedCards = [];
    gameState.matchedPairs = 0;
    gameState.attempts = 0;
    gameState.isProcessing = false;
    gameState.startTime = null;
    
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
        gameState.timerInterval = null;
    }

    // 타이머 리셋
    timerDisplay.textContent = '00:00';

    // 모달 닫기
    closeGameCompleteModal();
    closeLeaderboardModal();

    // 카드 쌍 생성 (이미지 인덱스 사용)
    const cardValues = [];
    for (let i = 0; i < config.pairs; i++) {
        cardValues.push(i, i); // 같은 이미지 인덱스를 두 번 추가
    }

    // Fisher-Yates 셔플 알고리즘
    for (let i = cardValues.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [cardValues[i], cardValues[j]] = [cardValues[j], cardValues[i]];
    }

    // 카드 상태 생성
    gameState.cards = cardValues.map((imageIndex, index) => ({
        id: index,
        value: imageIndex, // 이미지 인덱스 저장
        image: currentCardImages[imageIndex], // 현재 선택된 이미지 세트에서 가져오기
        isFlipped: false,
        isMatched: false
    }));

    renderGame();
    updateDisplay();
}

// 게임 보드 렌더링
function renderGame() {
    gameBoard.innerHTML = '';
    const config = difficultyConfig[gameState.difficulty];
    
    // 게임 보드 클래스 설정
    gameBoard.className = `game-board ${gameState.difficulty}`;

    gameState.cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        if (card.isFlipped) cardElement.classList.add('flipped');
        if (card.isMatched) cardElement.classList.add('matched');
        
        cardElement.innerHTML = `
            <div class="card-inner">
                <div class="card-front">?</div>
                <div class="card-back">
                    <span class="card-image">${card.image}</span>
                    ${card.isMatched ? '<span class="match-check">✓</span>' : ''}
                </div>
            </div>
        `;

        cardElement.addEventListener('click', () => handleCardClick(card.id));
        gameBoard.appendChild(cardElement);
    });
}

// 카드 클릭 처리
function handleCardClick(cardId) {
    if (gameState.isProcessing) return;

    const card = gameState.cards[cardId];
    if (card.isFlipped || card.isMatched) return;

    // 게임 시작 시간 기록
    if (gameState.startTime === null) {
        gameState.startTime = Date.now();
        startTimer();
    }

    // 카드 뒤집기
    card.isFlipped = true;
    gameState.flippedCards.push(cardId);
    renderGame();

    // 2장이 뒤집혔을 때 매칭 검사
    if (gameState.flippedCards.length === 2) {
        gameState.isProcessing = true;
        gameState.attempts++;
        updateDisplay();

        setTimeout(() => {
            checkMatch();
        }, 500);
    }
}

// 매칭 검사
function checkMatch() {
    const [firstId, secondId] = gameState.flippedCards;
    const firstCard = gameState.cards[firstId];
    const secondCard = gameState.cards[secondId];

    if (firstCard.value === secondCard.value) {
        // 매칭 성공
        firstCard.isMatched = true;
        secondCard.isMatched = true;
        gameState.matchedPairs++;

        // 게임 완료 확인
        const config = difficultyConfig[gameState.difficulty];
        if (gameState.matchedPairs === config.pairs) {
            setTimeout(() => {
                endGame();
            }, 500);
        }
    } else {
        // 매칭 실패 - 카드 다시 뒤집기
        firstCard.isFlipped = false;
        secondCard.isFlipped = false;
    }

    gameState.flippedCards = [];
    gameState.isProcessing = false;
    renderGame();
}

// 타이머 시작
function startTimer() {
    gameState.timerInterval = setInterval(() => {
        if (gameState.startTime) {
            const elapsed = Math.floor((Date.now() - gameState.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
            const seconds = (elapsed % 60).toString().padStart(2, '0');
            timerDisplay.textContent = `${minutes}:${seconds}`;
        }
    }, 1000);
}

// 게임 종료
function endGame() {
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
        gameState.timerInterval = null;
    }

    const elapsed = Math.floor((Date.now() - gameState.startTime) / 1000);
    const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const seconds = (elapsed % 60).toString().padStart(2, '0');

    document.getElementById('finalAttempts').textContent = gameState.attempts;
    document.getElementById('finalTime').textContent = `${minutes}:${seconds}`;
    
    gameCompleteModal.classList.add('show');
    playerNameInput.value = '';
}

// 화면 업데이트
function updateDisplay() {
    attemptsDisplay.textContent = gameState.attempts;
}

// 로컬 스토리지에 점수 저장
function saveScoreToLocal(scoreData) {
    try {
        const scores = JSON.parse(localStorage.getItem('game_scores') || '[]');
        scores.push({
            ...scoreData,
            id: Date.now().toString(),
            created_at: new Date().toISOString()
        });
        // 최신 100개만 유지
        scores.sort((a, b) => {
            if (a.attempts !== b.attempts) return a.attempts - b.attempts;
            return a.time_seconds - b.time_seconds;
        });
        localStorage.setItem('game_scores', JSON.stringify(scores.slice(0, 100)));
        return true;
    } catch (error) {
        console.error('로컬 스토리지 저장 오류:', error);
        return false;
    }
}

// 점수 저장
async function saveScore() {
    const elapsed = Math.floor((Date.now() - gameState.startTime) / 1000);
    const playerName = playerNameInput.value.trim() || '익명';

    // 로컬 스토리지용 데이터 (모든 정보 포함)
    const localScoreData = {
        player_name: playerName,
        attempts: gameState.attempts,
        time_seconds: elapsed,
        difficulty: gameState.difficulty
    };

    // Supabase용 데이터 (테이블 구조에 맞춤: turns만 사용)
    const supabaseScoreData = {
        player_name: playerName,
        turns: gameState.attempts  // attempts → turns로 매핑
    };

    let saved = false;

    // Supabase에 저장 시도
    if (supabaseClient) {
        try {
            const { data, error } = await supabaseClient
                .from('game_scores')
                .insert([supabaseScoreData])
                .select();

            if (error) throw error;
            saved = true;
            console.log('Supabase에 점수 저장 성공:', data);
        } catch (error) {
            console.error('Supabase 점수 저장 오류:', error);
            alert('Supabase 점수 저장에 실패했습니다: ' + error.message);
            // Supabase 실패 시 로컬 스토리지로 폴백
        }
    }

    // 로컬 스토리지에도 저장 (백업, 모든 정보 포함)
    if (saveScoreToLocal(localScoreData)) {
        if (!saved) saved = true; // Supabase 저장 실패 시에만 saved를 true로 설정
    }

    if (saved) {
        closeGameCompleteModal();
        // 자동으로 리더보드 열기 (현재 게임 난이도로 필터링)
        setTimeout(() => {
            leaderboardModal.classList.add('show');
            // 현재 게임 난이도 탭 활성화
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.difficulty === gameState.difficulty) {
                    btn.classList.add('active');
                }
            });
            loadLeaderboard(gameState.difficulty);
        }, 300);
    } else {
        alert('점수 저장에 실패했습니다.');
    }
}

// 날짜 포맷팅 함수
function formatDate(dateString) {
    if (!dateString) return '';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return '방금 전';
        if (diffMins < 60) return `${diffMins}분 전`;
        if (diffHours < 24) return `${diffHours}시간 전`;
        if (diffDays < 7) return `${diffDays}일 전`;
        
        // 일주일 이상이면 날짜 표시
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const mins = String(date.getMinutes()).padStart(2, '0');
        
        if (year === now.getFullYear()) {
            return `${month}/${day} ${hours}:${mins}`;
        }
        return `${year}/${month}/${day}`;
    } catch (e) {
        return '';
    }
}

// 리더보드 조회
async function loadLeaderboard(selectedDifficulty = 'all') {
    const leaderboardList = document.getElementById('leaderboardList');
    leaderboardList.innerHTML = '<p class="loading">로딩 중...</p>';

    let scores = [];
    let fromSupabase = false;

    // Supabase에서 조회 시도
    if (supabaseClient) {
        try {
            const { data, error } = await supabaseClient
                .from('game_scores')
                .select('*')
                .order('turns', { ascending: true })  // attempts → turns로 변경
                .limit(10);

            if (!error && data && data.length > 0) {
                // Supabase 데이터를 표준 형식으로 변환
                scores = data.map(score => ({
                    player_name: score.player_name,
                    attempts: score.turns,  // turns → attempts로 변환
                    time_seconds: null,  // Supabase 테이블에 없음
                    difficulty: null,  // Supabase 테이블에 없음
                    created_at: score.created_at
                }));
                fromSupabase = true;
            }
        } catch (error) {
            console.error('Supabase 리더보드 조회 오류:', error);
        }
    }

    // 로컬 스토리지에서 조회 (Supabase가 없거나 실패한 경우, 또는 난이도 필터링이 필요한 경우)
    if (!fromSupabase || selectedDifficulty !== 'all') {
        try {
            let localScores = JSON.parse(localStorage.getItem('game_scores') || '[]');
            
            // 난이도 필터링
            if (selectedDifficulty !== 'all') {
                localScores = localScores.filter(score => score.difficulty === selectedDifficulty);
            }
            
            // 정렬: 시도 횟수 오름차순, 시간 오름차순
            localScores.sort((a, b) => {
                if (a.attempts !== b.attempts) return a.attempts - b.attempts;
                if (a.time_seconds && b.time_seconds) {
                    return a.time_seconds - b.time_seconds;
                }
                return 0;
            });
            
            // Supabase 데이터가 있고 난이도가 'all'이면 Supabase 우선, 아니면 로컬 스토리지 사용
            if (!fromSupabase || selectedDifficulty !== 'all') {
                scores = localScores.slice(0, 10);
                fromSupabase = false;
            }
        } catch (error) {
            console.error('로컬 스토리지 조회 오류:', error);
        }
    }

    // 리더보드 표시
    if (scores.length === 0) {
        const difficultyText = selectedDifficulty === 'all' ? '' : ` (${{easy: '쉬움', medium: '보통', hard: '어려움'}[selectedDifficulty] || selectedDifficulty})`;
        leaderboardList.innerHTML = `<p class="empty-leaderboard">아직 기록이 없습니다${difficultyText}.<br>게임을 완료하면 기록이 저장됩니다!</p>`;
        return;
    }

    leaderboardList.innerHTML = scores.map((score, index) => {
        // 시간 표시 (time_seconds가 있는 경우만)
        const timeDisplay = score.time_seconds 
            ? `${Math.floor(score.time_seconds / 60).toString().padStart(2, '0')}:${(score.time_seconds % 60).toString().padStart(2, '0')}`
            : '-';
        
        const difficultyNames = { easy: '쉬움', medium: '보통', hard: '어려움' };
        const completedAt = formatDate(score.created_at);
        
        // 난이도 표시 (difficulty가 있는 경우만)
        const difficultyDisplay = score.difficulty 
            ? ` | ${difficultyNames[score.difficulty] || score.difficulty}`
            : '';
        
        let rankClass = '';
        if (index === 0) rankClass = 'rank-1';
        else if (index === 1) rankClass = 'rank-2';
        else if (index === 2) rankClass = 'rank-3';

        return `
            <div class="leaderboard-item ${rankClass}">
                <div class="leaderboard-rank">#${index + 1}</div>
                <div class="leaderboard-info">
                    <div class="leaderboard-name">${score.player_name || '익명'}</div>
                    <div class="leaderboard-stats">
                        시도: ${score.attempts}회${difficultyDisplay}
                        ${completedAt ? `<br><span class="leaderboard-date">${completedAt}</span>` : ''}
                    </div>
                </div>
                <div class="leaderboard-time">${timeDisplay}</div>
            </div>
        `;
    }).join('');
}

// 모달 닫기
function closeGameCompleteModal() {
    gameCompleteModal.classList.remove('show');
}

function closeLeaderboardModal() {
    leaderboardModal.classList.remove('show');
}

// 이벤트 리스너
newGameBtn.addEventListener('click', () => {
    initGame();
});

difficultySelect.addEventListener('change', (e) => {
    gameState.difficulty = e.target.value;
    initGame();
});

cardThemeSelect.addEventListener('change', (e) => {
    const theme = e.target.value;
    currentCardImages = cardImageSets[theme] || cardImageSets.fruits;
    initGame();
});

leaderboardBtn.addEventListener('click', () => {
    leaderboardModal.classList.add('show');
    // 기본적으로 "전체" 탭 활성화
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.difficulty === 'all') {
            btn.classList.add('active');
        }
    });
    loadLeaderboard('all');
});

// 리더보드 탭 클릭 이벤트
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('tab-btn')) {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        const difficulty = e.target.dataset.difficulty;
        loadLeaderboard(difficulty);
    }
});

saveScoreBtn.addEventListener('click', saveScore);

closeModalBtn.addEventListener('click', closeGameCompleteModal);

closeLeaderboardBtn.addEventListener('click', closeLeaderboardModal);

// 모달 외부 클릭 시 닫기
gameCompleteModal.addEventListener('click', (e) => {
    if (e.target === gameCompleteModal) {
        closeGameCompleteModal();
    }
});

leaderboardModal.addEventListener('click', (e) => {
    if (e.target === leaderboardModal) {
        closeLeaderboardModal();
    }
});

// Enter 키로 점수 저장
playerNameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        saveScore();
    }
});

// 게임 초기화
initGame();
