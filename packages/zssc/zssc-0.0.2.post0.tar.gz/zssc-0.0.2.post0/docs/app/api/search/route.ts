import { source } from '@/lib/source';
import { createFromSource } from 'fumadocs-core/search/server';

// Ensure the route is treated as static
export const revalidate = false;

export const { staticGET: GET } = createFromSource(source);
