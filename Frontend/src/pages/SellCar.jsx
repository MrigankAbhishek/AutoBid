import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';

const API = "http://127.0.0.1:5000";

export default function SellCar() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [images, setImages] = useState([]);
  const [previews, setPreviews] = useState([]);

  const [predictedModel, setPredictedModel] = useState(null);
  const [vin, setVin] = useState("");
  const [vinData, setVinData] = useState(null);
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState("");
  const [listed, setListed] = useState(false);

  const [formData, setFormData] = useState({
    fuel: "",
    transmission: "",
    city: "",
    km: ""
  });

  const handleImageChange = (e) => {
    const files = [...e.target.files];
    setImages(files);
    setPreviews(files.map(f => URL.createObjectURL(f)));
  };

  const detectModel = async () => {
    setLoading("Detecting model...");
    const data = new FormData();
    images.forEach(img => data.append("images", img));

    const res = await fetch(`${API}/predict-model`, {
      method: "POST",
      body: data
    });

    const result = await res.json();
    setPredictedModel(result.predicted_model);
    setLoading("");
  };

  const verifyVin = async () => {
    setLoading("Verifying VIN...");
    const res = await fetch(`${API}/verify-vin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        vin,
        predicted_model: predictedModel
      })
    });

    const result = await res.json();
    setVinData(result);
    setLoading("");
  };

  const analyzeDamage = async () => {
    setLoading("Analyzing damage & price...");
    const data = new FormData();

    images.forEach(img => data.append("images", img));
    data.append("model", predictedModel);
    data.append("year", vinData.year);
    data.append("fuel", formData.fuel);
    data.append("km", formData.km);
    data.append("transmission", formData.transmission);
    data.append("city", formData.city);

    const res = await fetch(`${API}/analyze-damage-price`, {
      method: "POST",
      body: data
    });

    const result = await res.json();
    setPriceData(result);
    setLoading("");
  };

  const listForAuction = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    setLoading("Listing for auction...");
    try {
      // Upload first image to Supabase Storage
      const file = images[0];
      const fileExt = file.name.split('.').pop();
      const fileName = `${Date.now()}-${Math.random().toString(36).substring(7)}.${fileExt}`;
      const filePath = `auction-images/${fileName}`;
      const { error: uploadError } = await supabase.storage
        .from('car-images')
        .upload(filePath, file);
      let imageUrl = '';
      if (uploadError) {
        // If storage isn't set up, use a preview URL or placeholder
        console.error('Upload error:', uploadError);
        imageUrl = previews[0] || '/placeholder.svg';
      } else {
        const { data: urlData } = supabase.storage
          .from('car-images')
          .getPublicUrl(filePath);
        imageUrl = urlData.publicUrl;
      }
      // Insert auction into database
      const { error: insertError } = await supabase
        .from('cars')
        .insert({
          title: `${vinData?.year || ''} ${predictedModel}`.trim(),
          price: Math.round(priceData.final_price),
          image: imageUrl,
          mileage: `${Number(formData.km).toLocaleString()} km`
        });
      if (insertError) {
        console.error('Insert error:', insertError);
        setLoading("");
        return;
      }
      setListed(true);
      setLoading("");
    } catch (err) {
      console.error('Listing error:', err);
      setLoading("");
    }
  };


  return (
    <div className="min-h-screen pt-24 pb-16 px-6">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-10 opacity-0 animate-fade-up">
          <h1 className="section-title text-foreground">
            Sell Your <span className="gold-text">Car</span>
          </h1>
          <p className="text-muted-foreground mt-2">AI-powered pricing and damage analysis</p>
        </div>

        <div className="glass-card p-8 flex flex-col gap-6 opacity-0 animate-fade-up" style={{ animationDelay: '100ms' }}>

          {/* Step 1: Upload Images */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
              Step 1 — Upload 4 Images
            </label>
            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/40 transition-colors cursor-pointer relative">
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleImageChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <p className="text-muted-foreground text-sm">
                {previews.length > 0 ? `${previews.length} photo(s) selected` : 'Click or drag photos here'}
              </p>
            </div>
            {previews.length > 0 && (
              <div className="flex gap-3 mt-4">
                {previews.map((src, i) => (
                  <img key={i} src={src} alt={`Preview ${i + 1}`} className="w-20 h-16 object-cover rounded-lg border border-border" />
                ))}
              </div>
            )}
            {images.length > 0 && !predictedModel && (
              <button className="btn-primary w-full mt-4" onClick={detectModel} disabled={!!loading}>
                {loading || "Detect Model"}
              </button>
            )}
          </div>

          {/* Step 2: Model Detected */}
          {predictedModel && (
            <div className="p-4 rounded-lg border border-primary/30 bg-primary/5">
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Detected Model</p>
              <p className="text-lg font-bold gold-text font-display">{predictedModel}</p>
            </div>
          )}

          {/* Step 3: VIN Verification */}
          {predictedModel && !vinData && (
            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">
                Step 2 — Enter VIN
              </label>
              <input
                value={vin}
                onChange={(e) => setVin(e.target.value)}
                placeholder="Enter 17-character VIN"
                className="input-field font-mono tracking-widest uppercase mb-4"
                maxLength={17}
              />
              <button className="btn-primary w-full" onClick={verifyVin} disabled={!!loading}>
                {loading || "Verify VIN"}
              </button>
            </div>
          )}

          {/* Step 4: VIN Verified + Details */}
          {vinData && vinData.verified && (
            <>
              <div className="p-4 rounded-lg border border-green-500/30 bg-green-500/5">
                <p className="text-sm font-semibold text-green-400 mb-2">✅ VIN Verified</p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <p className="text-muted-foreground">Manufacturer: <span className="text-foreground font-medium">{vinData.manufacturer}</span></p>
                  <p className="text-muted-foreground">Year: <span className="text-foreground font-medium">{vinData.year}</span></p>
                </div>
              </div>

              {!priceData && (
                <div>
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 block">
                    Step 3 — Enter Details
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">Fuel Type</label>
                      <input placeholder="Petrol / Diesel / EV" className="input-field" onChange={(e) => setFormData({ ...formData, fuel: e.target.value })} />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">Transmission</label>
                      <input placeholder="Auto / Manual" className="input-field" onChange={(e) => setFormData({ ...formData, transmission: e.target.value })} />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">City</label>
                      <input placeholder="Your city" className="input-field" onChange={(e) => setFormData({ ...formData, city: e.target.value })} />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2 block">KM Driven</label>
                      <input placeholder="e.g. 25000" className="input-field" onChange={(e) => setFormData({ ...formData, km: e.target.value })} />
                    </div>
                  </div>
                  <button className="btn-primary w-full mt-4" onClick={analyzeDamage} disabled={!!loading}>
                    {loading || "Analyze & Get Price"}
                  </button>
                </div>
              )}
            </>
          )}

          {/* Step 5: Price Result + List Button */}
          {priceData && !listed && (
            <div className="p-6 rounded-lg gold-glow border border-primary/30 bg-primary/5 text-center">
              <h3 className="text-lg font-display font-bold text-foreground mb-4">Damage Report</h3>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 rounded-lg bg-secondary">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">Dents</p>
                  <p className="text-xl font-bold text-foreground">{priceData.dents}</p>
                </div>
                <div className="p-3 rounded-lg bg-secondary">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">Scratches</p>
                  <p className="text-xl font-bold text-foreground">{priceData.scratches}</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Suggested Price</p>
              <p className="text-4xl font-display font-bold gold-text mb-6">
                ₹{Math.round(priceData.final_price).toLocaleString()}
              </p>
              <button className="btn-primary w-full" onClick={listForAuction} disabled={!!loading}>
                {loading || "List for Auction"}
              </button>
            </div>
          )}
          {/* Listed Success */}
          {listed && (
            <div className="p-6 rounded-lg border border-green-500/30 bg-green-500/5 text-center">
              <p className="text-2xl mb-2">🎉</p>
              <h3 className="text-lg font-display font-bold text-green-400 mb-2">Listed Successfully!</h3>
              <p className="text-sm text-muted-foreground mb-4">Your car is now live on the auction page.</p>
              <button className="btn-primary" onClick={() => navigate('/')}>
                View Auctions
              </button>
            </div>
          )}

          {/* Loading indicator */}
          {loading && (
            <div className="text-center py-2">
              <p className="text-sm text-primary animate-pulse">{loading}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
