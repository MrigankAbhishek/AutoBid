import React from 'react';

export default function AuctionCard({ item, onBid, index = 0 }) {
  return (
    <div
      className="glass-card card-hover overflow-hidden opacity-0 animate-fade-up"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="relative overflow-hidden">
        <img
          src={item.image}
          alt={item.title}
          className="w-full h-52 object-cover transition-transform duration-500 hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
        <div className="absolute bottom-3 left-3">
          <p className="text-xs text-muted-foreground">{item.mileage}</p>
        </div>
      </div>

      <div className="p-5">
        <h3 className="font-display font-bold text-lg text-foreground mb-4">{item.title}</h3>

        <div className="flex justify-between items-end mb-4">
          <div>
             <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Current Price</p>
            <p className="text-2xl font-bold gold-text">₹{item.price?.toLocaleString()}</p>
          </div>
        </div>

        <button
          className="btn-primary w-full text-sm"
          onClick={() => onBid && onBid(item.id)}
        >
          Place Bid (+₹10)
        </button>
      </div>
    </div>
  );
}
