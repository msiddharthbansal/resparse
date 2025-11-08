CREATE TABLE IF NOT EXISTS journals (
    journal_id SERIAL PRIMARY KEY,
    journal_name VARCHAR(500) NOT NULL UNIQUE,
    journal_abbr VARCHAR(100),
    journal_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS journal_metrics (
    metric_id SERIAL PRIMARY KEY,
    journal_id INTEGER NOT NULL REFERENCES journals(journal_id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    jif DECIMAL(10, 3),
    jif_5years DECIMAL(10, 3),
    quartile VARCHAR(2),
    ranking INTEGER,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (journal_id, year)
);

CREATE TABLE IF NOT EXISTS journal_categories (
    journal_category_id SERIAL PRIMARY KEY,
    journal_id INTEGER NOT NULL REFERENCES journals(journal_id) ON DELETE CASCADE,
    category_name VARCHAR(255) NOT NULL,
    UNIQUE (journal_id, category_name)
);

CREATE TABLE IF NOT EXISTS papers (
    paper_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    doi VARCHAR(255) UNIQUE,
    journal_id INTEGER REFERENCES journals(journal_id),
    publication_date DATE,
    publication_year INTEGER,
    volume VARCHAR(20),
    issue VARCHAR(20),
    abstract TEXT,
    keywords TEXT,
    pdf_url TEXT,
    citation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS authors (
    author_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    affiliation VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paper_authors (
    paper_author_id SERIAL PRIMARY KEY,
    paper_id INTEGER NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES authors(author_id),
    author_position INTEGER,
    UNIQUE(paper_id, author_id)
);

CREATE INDEX IF NOT EXISTS idx_papers_journal ON papers(journal_id);
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(publication_year);
CREATE INDEX IF NOT EXISTS idx_papers_date ON papers(publication_date);
CREATE INDEX IF NOT EXISTS idx_journal_metrics_current ON journal_metrics(is_current);
CREATE INDEX IF NOT EXISTS idx_journal_categories_category ON journal_categories(category_name);
CREATE INDEX IF NOT EXISTS idx_paper_authors_paper ON paper_authors(paper_id);
CREATE INDEX IF NOT EXISTS idx_paper_authors_author ON paper_authors(author_id);