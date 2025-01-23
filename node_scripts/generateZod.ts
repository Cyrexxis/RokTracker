import { resolveRefs } from 'json-refs'
import jsonSchemaToZod from 'json-schema-to-zod'
import { pascalCase } from 'change-case'
import * as fs from 'fs'
import * as path from 'path'
import * as prettier from 'prettier'

const schemaDir = './schema'
const outputDir = './src/schema'

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true })
}

async function convertSchemas() {
  const files = fs.readdirSync(schemaDir)

  for (const file of files) {
    const filePath = path.join(schemaDir, file)
    const schema = JSON.parse(fs.readFileSync(filePath, 'utf-8'))

    const name = pascalCase(file.replace('.json', ''))

    const resolvedSchema = await resolveRefs(schema)
    const zodSchema = jsonSchemaToZod(resolvedSchema.resolved, {
      module: 'esm',
      type: name,
      name: name + 'Schema',
    })

    const zodFormatted = await prettier.format(zodSchema, { parser: 'typescript' })

    const outputFilePath = path.join(outputDir, name + '.ts')
    fs.writeFileSync(outputFilePath, zodFormatted)
  }
}

convertSchemas().catch(console.error)
