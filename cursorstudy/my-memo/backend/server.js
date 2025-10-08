const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('@prisma/client');

const app = express();
const prisma = new PrismaClient();
const PORT = process.env.PORT || 5001;
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// 미들웨어
app.use(cors({
  origin: ['http://localhost:3000', 'http://127.0.0.1:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());

// 요청 로깅 미들웨어
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  console.log('Headers:', req.headers);
  next();
});

// JWT 토큰 검증 미들웨어
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

// 회원가입
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;

    // 입력 검증
    if (!email || !password || !name) {
      return res.status(400).json({ error: '이메일, 비밀번호, 이름은 모두 필수입니다.' });
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ error: '올바른 이메일 형식이 아닙니다.' });
    }

    // 비밀번호 길이 검증
    if (password.length < 6) {
      return res.status(400).json({ error: '비밀번호는 최소 6자 이상이어야 합니다.' });
    }

    // 이름 길이 검증
    if (name.trim().length < 2) {
      return res.status(400).json({ error: '이름은 최소 2자 이상이어야 합니다.' });
    }

    // 이메일 중복 확인
    const existingUser = await prisma.user.findUnique({
      where: { email: email.toLowerCase() }
    });

    if (existingUser) {
      return res.status(400).json({ error: '이미 사용 중인 이메일입니다.' });
    }

    // 비밀번호 해시화
    const hashedPassword = await bcrypt.hash(password, 10);

    // 사용자 생성
    const user = await prisma.user.create({
      data: {
        email: email.toLowerCase(),
        password: hashedPassword,
        name: name.trim()
      }
    });

    // JWT 토큰 생성
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.status(201).json({
      message: 'User created successfully',
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 로그인
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    console.log('Login attempt for email:', email);

    // 입력 검증
    if (!email || !password) {
      console.log('Missing email or password');
      return res.status(400).json({ error: '이메일과 비밀번호는 필수입니다.' });
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      console.log('Invalid email format:', email);
      return res.status(400).json({ error: '올바른 이메일 형식이 아닙니다.' });
    }

    // 사용자 찾기
    const user = await prisma.user.findUnique({
      where: { email: email.toLowerCase() }
    });

    if (!user) {
      console.log('User not found for email:', email.toLowerCase());
      return res.status(401).json({ error: '이메일 또는 비밀번호가 올바르지 않습니다.' });
    }

    console.log('User found:', user.email);

    // 비밀번호 확인
    const isValidPassword = await bcrypt.compare(password, user.password);

    if (!isValidPassword) {
      console.log('Invalid password for user:', user.email);
      return res.status(401).json({ error: '이메일 또는 비밀번호가 올바르지 않습니다.' });
    }

    console.log('Password valid for user:', user.email);

    // JWT 토큰 생성
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.json({
      message: 'Login successful',
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 로그아웃 (클라이언트에서 토큰 제거)
app.post('/api/auth/logout', (req, res) => {
  res.json({ message: 'Logout successful' });
});

// 사용자 정보 조회
app.get('/api/auth/me', authenticateToken, async (req, res) => {
  try {
    const user = await prisma.user.findUnique({
      where: { id: req.user.userId },
      select: {
        id: true,
        email: true,
        name: true,
        createdAt: true
      }
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 메모 관련 API
// 모든 메모 조회
app.get('/api/memos', authenticateToken, async (req, res) => {
  try {
    const memos = await prisma.memo.findMany({
      where: { userId: req.user.userId },
      orderBy: { updatedAt: 'desc' }
    });

    // tags를 JSON 문자열에서 배열로 변환
    const memosWithParsedTags = memos.map(memo => ({
      ...memo,
      tags: memo.tags ? JSON.parse(memo.tags) : []
    }));

    res.json(memosWithParsedTags);
  } catch (error) {
    console.error('Get memos error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 새 메모 생성
app.post('/api/memos', authenticateToken, async (req, res) => {
  try {
    const { title, content, tags, color } = req.body;

    const memo = await prisma.memo.create({
      data: {
        title: title || '제목 없음',
        content: content || '',
        tags: tags ? JSON.stringify(tags) : null,
        color: color || '#ffffff',
        userId: req.user.userId
      }
    });

    res.status(201).json({
      ...memo,
      tags: memo.tags ? JSON.parse(memo.tags) : []
    });
  } catch (error) {
    console.error('Create memo error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 메모 수정
app.put('/api/memos/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const { title, content, tags, color } = req.body;

    // 메모 소유권 확인
    const existingMemo = await prisma.memo.findFirst({
      where: { id, userId: req.user.userId }
    });

    if (!existingMemo) {
      return res.status(404).json({ error: 'Memo not found' });
    }

    const memo = await prisma.memo.update({
      where: { id },
      data: {
        title: title || '제목 없음',
        content: content || '',
        tags: tags ? JSON.stringify(tags) : null,
        color: color || '#ffffff'
      }
    });

    res.json({
      ...memo,
      tags: memo.tags ? JSON.parse(memo.tags) : []
    });
  } catch (error) {
    console.error('Update memo error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 메모 삭제
app.delete('/api/memos/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;

    // 메모 소유권 확인
    const existingMemo = await prisma.memo.findFirst({
      where: { id, userId: req.user.userId }
    });

    if (!existingMemo) {
      return res.status(404).json({ error: 'Memo not found' });
    }

    await prisma.memo.delete({
      where: { id }
    });

    res.json({ message: 'Memo deleted successfully' });
  } catch (error) {
    console.error('Delete memo error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 서버 시작
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
  await prisma.$disconnect();
  process.exit(0);
});
