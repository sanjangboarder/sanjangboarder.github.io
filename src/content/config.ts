import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    category: z.string().optional().default('미분류'),
    categoryNo: z.coerce.number().optional().default(0),
    logNo: z.coerce.number().optional(),
    source: z.string().optional(),
    thumbnail: z.string().optional().default(''),
    description: z.string().optional().default(''),
    lang: z.enum(['ko', 'en']).optional().default('ko'),
  }),
});

export const collections = { posts };
