import { GoogleGenAI } from "@google/genai";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "fs";
import fsp from "fs/promises";
import path from "path";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
if (!GEMINI_API_KEY) {
  console.error("Error: GEMINI_API_KEY environment variable is required");
  process.exit(1);
}

const OUTPUT_DIR =
  process.env.IMAGE_OUTPUT_DIR ?? path.join(process.cwd(), "generated-images");

const MODEL = process.env.GEMINI_IMAGE_MODEL ?? "gemini-2.0-flash-exp";

// ---------------------------------------------------------------------------
// Gemini client
// ---------------------------------------------------------------------------

const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

// ---------------------------------------------------------------------------
// MCP server
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "gemini-image",
  version: "1.0.0",
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Ensure the output directory exists (idempotent).
 */
async function ensureOutputDir() {
  await fsp.mkdir(OUTPUT_DIR, { recursive: true });
}

/**
 * Derive a file extension from a MIME type string.
 * Falls back to "png" for unknown types.
 */
function extFromMimeType(mimeType = "") {
  if (mimeType.includes("jpeg") || mimeType.includes("jpg")) return "jpg";
  if (mimeType.includes("webp")) return "webp";
  if (mimeType.includes("gif")) return "gif";
  return "png";
}

/**
 * Detect a MIME type from a file extension.
 */
function mimeFromExt(ext = "") {
  const lower = ext.replace(/^\./, "").toLowerCase();
  switch (lower) {
    case "jpg":
    case "jpeg":
      return "image/jpeg";
    case "webp":
      return "image/webp";
    case "gif":
      return "image/gif";
    default:
      return "image/png";
  }
}

/**
 * Build a unique output path, appending a numeric suffix if the file already
 * exists (e.g. "foo.png", "foo-1.png", "foo-2.png", …).
 */
async function uniqueOutputPath(base, ext) {
  let candidate = path.join(OUTPUT_DIR, `${base}.${ext}`);
  let counter = 0;
  while (fs.existsSync(candidate)) {
    counter += 1;
    candidate = path.join(OUTPUT_DIR, `${base}-${counter}.${ext}`);
  }
  return candidate;
}

/**
 * Save all inlineData parts from a Gemini response to disk.
 * Returns an array of absolute file paths for every image written.
 */
async function saveInlineImages(parts, baseFilename) {
  await ensureOutputDir();
  const saved = [];

  for (const part of parts) {
    if (!part.inlineData) continue;

    const ext = extFromMimeType(part.inlineData.mimeType);
    const outputPath = await uniqueOutputPath(baseFilename, ext);
    const buffer = Buffer.from(part.inlineData.data, "base64");
    await fsp.writeFile(outputPath, buffer);
    saved.push(outputPath);
  }

  return saved;
}

/**
 * Extract plain-text content from Gemini response parts.
 */
function extractText(parts) {
  return parts
    .filter((p) => p.text)
    .map((p) => p.text)
    .join("\n")
    .trim();
}

// ---------------------------------------------------------------------------
// Tool: generate_image
// ---------------------------------------------------------------------------

server.tool(
  "generate_image",
  "Generate an image from a text prompt using Gemini's image generation capabilities. Returns the file path of the saved image.",
  {
    prompt: z.string().describe("Text description of the image to generate"),
    filename: z
      .string()
      .optional()
      .describe(
        "Optional base filename for the output (without extension). Defaults to a timestamp-based name."
      ),
    width: z.number().int().positive().optional().describe("Optional image width in pixels"),
    height: z.number().int().positive().optional().describe("Optional image height in pixels"),
  },
  async ({ prompt, filename, width, height }) => {
    try {
      const generationConfig = {
        responseModalities: ["image", "text"],
      };

      if (width && height) {
        generationConfig.imageSize = { width, height };
      }

      const response = await ai.models.generateContent({
        model: MODEL,
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        config: generationConfig,
      });

      const parts = response.candidates?.[0]?.content?.parts ?? [];
      const baseFilename = filename ?? `gemini-${Date.now()}`;
      const savedFiles = await saveInlineImages(parts, baseFilename);

      if (savedFiles.length === 0) {
        const modelText = extractText(parts);
        return {
          content: [
            {
              type: "text",
              text: `Image generation did not return an image.\n\nModel response: ${modelText || "(none)"}`,
            },
          ],
          isError: true,
        };
      }

      return {
        content: [
          {
            type: "text",
            text: [
              "Image generated successfully!",
              "",
              `Saved to: ${savedFiles.join(", ")}`,
              `Prompt: "${prompt}"`,
            ].join("\n"),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error generating image: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: edit_image
// ---------------------------------------------------------------------------

server.tool(
  "edit_image",
  "Edit an existing image using a text prompt. Provide the image path and instructions for how to modify it.",
  {
    imagePath: z.string().describe("Absolute or relative path to the source image to edit"),
    prompt: z.string().describe("Instructions describing how to edit the image"),
    filename: z
      .string()
      .optional()
      .describe("Optional base filename for the output (without extension)"),
  },
  async ({ imagePath, prompt, filename }) => {
    try {
      if (!fs.existsSync(imagePath)) {
        return {
          content: [
            {
              type: "text",
              text: `Error: Source image not found at path: ${imagePath}`,
            },
          ],
          isError: true,
        };
      }

      const ext = path.extname(imagePath).slice(1);
      const mimeType = mimeFromExt(ext);

      const imageBuffer = await fsp.readFile(imagePath);
      const base64Image = imageBuffer.toString("base64");

      const response = await ai.models.generateContent({
        model: MODEL,
        contents: [
          {
            role: "user",
            parts: [
              { text: prompt },
              { inlineData: { mimeType, data: base64Image } },
            ],
          },
        ],
        config: {
          responseModalities: ["image", "text"],
        },
      });

      const parts = response.candidates?.[0]?.content?.parts ?? [];
      const baseFilename = filename ?? `gemini-edit-${Date.now()}`;
      const savedFiles = await saveInlineImages(parts, baseFilename);

      if (savedFiles.length === 0) {
        const modelText = extractText(parts);
        return {
          content: [
            {
              type: "text",
              text: `Image edit did not return an image.\n\nModel response: ${modelText || "(none)"}`,
            },
          ],
          isError: true,
        };
      }

      return {
        content: [
          {
            type: "text",
            text: [
              "Image edited successfully!",
              "",
              `Saved to: ${savedFiles.join(", ")}`,
              `Source: ${imagePath}`,
              `Edit prompt: "${prompt}"`,
            ].join("\n"),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error editing image: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Start server
// ---------------------------------------------------------------------------

const transport = new StdioServerTransport();

try {
  await server.connect(transport);
} catch (err) {
  console.error("Fatal: failed to start MCP server:", err.message);
  process.exit(1);
}
