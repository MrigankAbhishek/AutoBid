import React, { useState, useEffect } from 'react';
import AuctionCard from '../components/AuctionCard';
import { supabase } from '../lib/supabase';
import heroBg from '../assets/hero-bg.jpg';

export default function Home() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAuctions = async () => {
      const { data, error } = await supabase
        .from('cars')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching auctions:', error);
      } else {
        setItems(data || []);
      }
      setLoading(false);
    };

    fetchAuctions();
  }, []);

  const handleBid = (id) => {
    setItems(prev =>
      prev.map(item =>
        item.id === id ? { ...item, price: item.price + 10 } : item
      )
    );
  };

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative h-[70vh] flex items-center justify-center overflow-hidden">
        <img
          src={heroBg}
          alt="Luxury car showroom"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/40 via-background/60 to-background" />
        <div className="relative z-10 text-center px-6 max-w-3xl">
          <p className="text-sm uppercase tracking-[0.3em] text-primary font-semibold mb-4 opacity-0 animate-fade-up">
            Premium Car Auctions
          </p>
          <h1
            className="text-5xl md:text-7xl font-display font-bold mb-6 opacity-0 animate-fade-up text-foreground"
            style={{ animationDelay: '100ms' }}
          >
            Find Your <span className="gold-text">Dream Car</span>
          </h1>
          <p
            className="text-lg text-muted-foreground max-w-xl mx-auto mb-8 opacity-0 animate-fade-up"
            style={{ animationDelay: '200ms' }}
          >
            Bid on exclusive vehicles from the world's finest collections. Every car tells a story.
          </p>
          <div
            className="flex gap-4 justify-center opacity-0 animate-fade-up"
            style={{ animationDelay: '300ms' }}
          >
            <a href="#auctions" className="btn-primary">Browse Auctions</a>
            <a href="/sell" className="btn-outline">Sell Your Car</a>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-b border-border">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-3 gap-8 text-center">
          {[
            { value: '2,400+', label: 'Cars Sold' },
            { value: '$12M+', label: 'Total Bids' },
            { value: '98%', label: 'Satisfaction' },
          ].map((stat, i) => (
            <div key={i}>
              <p className="text-2xl md:text-3xl font-bold gold-text font-display">{stat.value}</p>
              <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Auction Grid */}
      <section id="auctions" className="max-w-7xl mx-auto px-6 py-16">
        <div className="flex items-center justify-between mb-10">
          <h2 className="section-title text-foreground">
            Live <span className="gold-text">Auctions</span>
          </h2>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-muted-foreground">{items.length} active</span>
          </div>
        </div>

        {loading ? (
          <p className="text-center text-muted-foreground animate-pulse">Loading auctions...</p>
        ) : items.length === 0 ? (
          <p className="text-center text-muted-foreground">No auctions found.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {items.map((item, i) => (
              <AuctionCard key={item.id} item={item} onBid={handleBid} index={i} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
