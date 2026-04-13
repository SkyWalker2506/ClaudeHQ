import { GoogleGenAI } from "@google/genai";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "fs";
import path from "path";

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
if (!GEMINI_API_KEY) {
  console.error("GEMINI_API_KEY environment variable is required");
  process.exit(1);
}

const OUTPUT_DIR = process.env.IMAGE_OUTPUT_DIR || path.join(process.cwd(), "generated-images");
const MODEL = process.env.GEMINI_IMAGE_MODEL || "gemini-2.0-flash-exp";

const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

const server = new McpServer({
  name: "gemini-image",
  version: "1.0.0",
});

server.tool(
  "generate_image",
  "Generate an image from a text prompt using Gemini's image generation capabilities. Returns the file path of the saved image.",
  {
    prompt: z.string().describe("Text description of the image to generate"),
    filename: z.string().optional().describe("Optional filename for the output (without extension). Defaults to a timestamp-based name."),
    width: z.number().optional().describe("Optional image width"),
    height: z.number().optional().describe("Optional image height"),
  },
  async ({ prompt, filename, width, height }) => {
    try {
      if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
      }

      const config = {
        responseModalities: ["image", "text"],
      };

      if (width && height) {
        config.imageSize = { width, height };
      }

      const response = await ai.models.generateContent({
        model: MODEL,
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        config,
      });

      const parts = response.candidates?.[0]?.content?.parts || [];
      const savedFiles = [];

      for (const part of parts) {
        if (part.inlineData) {
          const ext = part.inlineData.mimeType?.includes("png") ? "png" : "jpg";
          const outputFilename = filename
            ? `${filename}.${ext}`
            : `gemini-${Date.now()}.${ext}`;
          const outputPath = path.join(OUTPUT_DIR, outputFilename);

          const imageBuffer = Buffer.from(part.inlineData.data, "base64");
          fs.writeFileSync(outputPath, imageBuffer);
          savedFiles.push(outputPath);
        }
      }

      if (savedFiles.length === 0) {
        const textResponse = parts
          .filter((p) => p.text)
          .map((p) => p.text)
          .join("\n");
        return {
          content: [
            {
              type: "text",
              text: `Image generation did not return an image. Model response: ${textResponse || "No response"}`,
            },
          ],
        };
      }

      return {
        content: [
          {
            type: "text",
            text: `Image generated successfully!\n\nSaved to: ${savedFiles.join(", ")}\n\nPrompt used: "${prompt}"`,
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

server.tool(
  "edit_image",
  "Edit an existing image using a text prompt. Provide the image path and instructions for how to modify it.",
  {
    imagePath: z.string().describe("Path to the source image to edit"),
    prompt: z.string().describe("Instructions for how to edit the image"),
    filename: z.string().optional().describe("Optional filename for the output (without extension)"),
  },
  async ({ imagePath, prompt, filename }) => {
    try {
      if (!fs.existsSync(imagePath)) {
        return {
          content: [{ type: "text", text: `Error: Image not found at ${imagePath}` }],
          isError: true,
        };
      }

      if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
      }

      const imageData = fs.readFileSync(imagePath);
      const base64Image = imageData.toString("base64");
      const ext = path.extname(imagePath).slice(1) || "png";
      const mimeType = ext === "jpg" || ext === "jpeg" ? "image/jpeg" : "image/png";

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

      const parts = response.candidates?.[0]?.content?.parts || [];
      const savedFiles = [];

      for (const part of parts) {
        if (part.inlineData) {
          const outExt = part.inlineData.mimeType?.includes("png") ? "png" : "jpg";
          const outputFilename = filename
            ? `${filename}.${outExt}`
            : `gemini-edit-${Date.now()}.${outExt}`;
          const outputPath = path.join(OUTPUT_DIR, outputFilename);

          const imageBuffer = Buffer.from(part.inlineData.data, "base64");
          fs.writeFileSync(outputPath, imageBuffer);
          savedFiles.push(outputPath);
        }
      }

      if (savedFiles.length === 0) {
        const textResponse = parts.filter((p) => p.text).map((p) => p.text).join("\n");
        return {
          content: [{ type: "text", text: `Image edit did not return an image. Model response: ${textResponse || "No response"}` }],
        };
      }

      return {
        content: [
          {
            type: "text",
            text: `Image edited successfully!\n\nSaved to: ${savedFiles.join(", ")}\n\nEdit prompt: "${prompt}"`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Error editing image: ${error.message}` }],
        isError: true,
      };
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
