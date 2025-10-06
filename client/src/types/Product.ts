export interface Product {
  id: number;
  name: string;
  price: number;
  originalPrice?: number;
  discount?: number;
  rating?: number;
  soldCount?: number;
  image?: string;
  labels?: string[];
}
  