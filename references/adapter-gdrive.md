# Adapter: Google Drive

Translates standard data model operations into .md files with YAML front matter stored in Google Drive.

## File Format

**Identical to GitHub adapter**: .md files with YAML front matter. Same format, same structure. This means files are portable between GitHub and Google Drive — copy/move without conversion.

## Directory Structure

Mirror of the GitHub second-brain structure, as a folder hierarchy in Google Drive:

```
second-brain/          ← Root folder in Google Drive
├── inbox/
├── _meta/
├── projects/{name}/
├── areas/{name}/
├── wiki/
├── archive/
└── templates/
```

## Operations

All operations use Google Drive MCP tools.

### Save(type, data)
1. Generate filename from date + slugified title
2. Create .md content (front matter + body)
3. Upload to the correct folder path via Google Drive MCP

### Update(type, id, data)
1. Read existing file via Google Drive MCP
2. Parse front matter, merge changes
3. Update `last_modified` timestamp
4. Upload updated file (overwrite)

### Archive(type, id)
1. Move file to `archive/{original-path}/` via Google Drive MCP

### Read(type, id)
1. Download file via Google Drive MCP
2. Parse front matter + body
3. Return structured data

### List(type, filters)
1. List files in the type's folder via Google Drive MCP
2. Download and parse each file's front matter
3. Filter by specified field values

### Search(keyword)
1. Use Google Drive MCP search (fullText contains '{keyword}')
2. Download and parse matching files

### ReadProjectContext(project_id)
1. List and download all files under `projects/{project}/`

## Change Detection

For sync: Google Drive MCP query `modifiedTime > '{last_sync_time}'`

Returns list of files modified since last sync. Download and parse each.

## Deletion

Same as GitHub: mark in front matter `_deleted: true`. Do not actually delete from Drive until user confirms.

## No Git History

Google Drive does not have git history. Change detection relies solely on `modifiedTime`. Drive's built-in version history provides some recovery capability.

## Setup

User needs:
1. Google Drive MCP connected
2. A `second-brain` root folder created in Drive
3. Folder structure created (can be done by RETROSPECTIVE on first run)
