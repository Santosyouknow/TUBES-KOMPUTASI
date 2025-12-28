const express = require('express');
const { Pool } = require('pg');
const redis = require('redis');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = 3000;

// Security middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 menit
  max: 100 // maksimal 100 request per IP
});
app.use(limiter);

// PostgreSQL connection
const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: 5432,
});

async function createTodo(title, completed, description = '') {
  const query = {
    text: 'INSERT INTO todos (title, completed, description, created_at, updated_at) VALUES ($1, $2, $3, NOW(), NOW()) RETURNING *',
    values: [title, Boolean(completed), description],
  };
  const result = await pool.query(query);
  return result.rows[0];
}

// Redis connection
let redisClient;
(async () => {
  redisClient = redis.createClient({
    socket: {
      host: process.env.REDIS_HOST,
      port: 6379
    }
  });
  
  redisClient.on('error', (err) => console.log('Redis Client Error', err));
  await redisClient.connect();
  console.log('Connected to Redis');
})();

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy',
    instance: process.env.INSTANCE_NAME || 'unknown',
    timestamp: new Date().toISOString()
  });
});

async function getAllTodos() {
  const result = await pool.query('SELECT * FROM todos ORDER BY created_at DESC');
  return result.rows;
}

// Get all todos (dengan caching)
app.get('/todos', async (req, res) => {
  try {
    // Cek cache terlebih dahulu
    const cached = await redisClient.get('todos:all');
    if (cached) {
      return res.json({
        source: 'cache',
        instance: process.env.INSTANCE_NAME,
        data: JSON.parse(cached)
      });
    }

    // Jika tidak ada di cache, ambil dari database
    const todos = await getAllTodos();
    
    // Simpan ke cache selama 60 detik
    await redisClient.setEx('todos:all', 60, JSON.stringify(todos));
    
    res.json({
      source: 'database',
      instance: process.env.INSTANCE_NAME,
      data: todos
    });
  } catch (error) {
    console.error('Error fetching todos:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new todo
app.post('/todos', async (req, res) => {
  console.log('POST /todos request received');
  console.log('Request body:', req.body);
  console.log('Request headers:', req.headers);
  
  try {
    const { title, completed, description = '' } = req.body;
    
    console.log('Parsed data:', { title, completed, description, titleType: typeof title, completedType: typeof completed });
    
    if (!title) {
      console.log('Title validation failed');
      return res.status(400).json({ error: 'Title is required' });
    }

    console.log('Calling createTodo function...');
    const newTodo = await createTodo(title, completed, description);
    console.log('createTodo result:', newTodo);

    // Invalidate cache
    await redisClient.del('todos:all');

    res.status(201).json({
      instance: process.env.INSTANCE_NAME,
      data: newTodo
    });
  } catch (error) {
    console.error('Error creating todo:', error);
    console.error('Error stack:', error.stack);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Update todo status
app.patch('/todos/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { completed } = req.body;

    const result = await pool.query(
      'UPDATE todos SET completed = $1, updated_at = NOW() WHERE id = $2 RETURNING *',
      [completed, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Todo not found' });
    }

    // Invalidate cache
    await redisClient.del('todos:all');

    res.json({
      instance: process.env.INSTANCE_NAME,
      data: result.rows[0]
    });
  } catch (error) {
    console.error('Error updating todo:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete todo
app.delete('/todos/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query('DELETE FROM todos WHERE id = $1 RETURNING *', [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Todo not found' });
    }

    // Invalidate cache
    await redisClient.del('todos:all');

    res.json({
      instance: process.env.INSTANCE_NAME,
      message: 'Todo deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting todo:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Statistics endpoint
app.get('/stats', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE completed = true) as completed,
        COUNT(*) FILTER (WHERE completed = false) as pending
      FROM todos
    `);

    res.json({
      instance: process.env.INSTANCE_NAME,
      stats: result.rows[0]
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`${process.env.INSTANCE_NAME} running on port ${PORT}`);
});
