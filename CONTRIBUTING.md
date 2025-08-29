# Contributing to fruxAI

We welcome contributions to fruxAI! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/fruxAI.git`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Run tests: `python services/fruxAI/test-api.py`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📋 Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guide
- **JavaScript/HTML**: Use consistent formatting
- **Documentation**: Write clear, concise comments

### Commit Messages

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

Examples:
```
feat(api): add crawl job status endpoint
fix(worker): resolve memory leak in crawler
docs(readme): update installation instructions
```

### Branch Naming

- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes
- `hotfix/critical-fix`: Critical fixes
- `docs/documentation-update`: Documentation updates

## 🏗️ Project Structure

```
fruxAI/
├── services/fruxAI/          # Backend services
│   ├── api/                 # FastAPI application
│   ├── worker/              # Python crawler worker
│   ├── docker/              # Docker configurations
│   └── config/              # Configuration files
├── frontend/                # Frontend application
├── docs/                    # Documentation
├── .gitignore              # Git ignore rules
├── LICENSE                  # MIT License
└── README.md               # Project overview
```

## 🧪 Testing

### Backend Tests
```bash
cd services/fruxAI
python test-api.py
```

### Manual Testing
1. Start services: `docker-compose up -d`
2. Test API endpoints using curl or Postman
3. Verify frontend functionality

## 📝 Documentation

### API Documentation
- Update OpenAPI specs in `services/fruxAI/api/main.py`
- Document new endpoints with docstrings
- Update README files

### Frontend Documentation
- Update component documentation
- Add inline comments for complex logic
- Update user guides

## 🔧 Development Environment

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/fruxAI.git
cd fruxAI

# Start development environment
cd services/fruxAI
docker-compose up -d

# Run tests
python test-api.py
```

## 🐛 Reporting Issues

When reporting issues, please include:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant log files

## 💡 Feature Requests

For feature requests:
- Check existing issues first
- Provide detailed description
- Explain the use case
- Suggest implementation approach if possible

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Follow our community guidelines

## 📞 Getting Help

- **Documentation**: Check README files and docs/
- **Issues**: Use GitHub Issues for bugs and questions
- **Discussions**: Use GitHub Discussions for general questions

## 🎉 Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- README.md contributors section
- GitHub repository contributors

Thank you for contributing to fruxAI! 🚀
