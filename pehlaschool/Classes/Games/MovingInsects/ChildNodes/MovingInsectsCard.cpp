//
//  Card.cpp on Aug 3, 2016
//  TodoSchool
//
//  Copyright (c) 2016 Enuma, Inc. All rights reserved.
//  See LICENSE.md for more details.
//


#include "MovingInsectsCard.h"
#include "../Utils/MovingInsectsMainDepot.h"

BEGIN_NS_MOVINGINSECTS

namespace {
    string contentSkinFront() { return MainDepot().assetPrefix() + "/Card/moving_image_card-front.png"; }
    string contentSkinBack() { return MainDepot().assetPrefix() + "/Card/moving_image_card-back.png"; }
    Size contentSize() { return MainDepot().cardSize(); }

    float durationForCardShake() { return .375f; }
    float durationForCardFlip() { return .2f; }

    float titleFontSize() { return 220.f; }
    Color4B titleFontColor() { return Color4B(161, 90, 50, 255); }
}  // unnamed namespace


Card::Card()
: FrontFace(nullptr)
, TitleLabel(nullptr)
, BackFace(nullptr)
{
}

bool Card::init() {
    if (!Super::init()) { return false; }
 
    clearInternals();
    refreshChildNodes();

    return true;
}

void Card::setVisible(bool Visible) {
    Super::setVisible(Visible);
    
    setRotation3D(getRotation3D());  // XXX
}

void Card::setRotation3D(const Vec3& Rotation) {
    Super::setRotation3D(Rotation);
    Vec3 R = Rotation;
    
    // XXX: Can't we do this by using fmod?
    while (R.y > 360.f) { R.y -= 360.f; }
    while (R.y < 0.f) { R.y += 360.f; }
    
    
    // 0-f-90-b-180-b-270-f-360
    //
    // 270-360, 0-90: front
    // 90 - 180 - 270: back
    
    auto InRange = [](float Value, float Min, float Max) {
        return (Min <= Value && Value <= Max);
    };
    
    bool FrontV = true;
    bool BackV = true;
    
    if (InRange(R.y, 0.f, 90.f)) {
        BackV = false;
    }
    else if (InRange(R.y, 90.f, 180.f)) {
        FrontV = false;
    }
    else if (InRange(R.y, 180.f, 270.f)) {
        FrontV = false;
    }
    else if (InRange(R.y, 270.f, 360.f)) {
        BackV = false;
    }
    
    if (FrontFace)
        FrontFace->setVisible(isVisible() && FrontV);
    
    if (BackFace)
        BackFace->setVisible(isVisible() && BackV);
}

FiniteTimeAction* Card::movementGuard(FiniteTimeAction* Action) {
    Vector<FiniteTimeAction*> Actions;
    
    Actions.pushBack(actionForCleanUpRotation());
    Actions.pushBack(localZOrderGuard(Action));

    return Sequence::create(Actions);
}

FiniteTimeAction* Card::localZOrderGuard(FiniteTimeAction* Action) {
    Vector<FiniteTimeAction*> Actions;
    
    Actions.pushBack(CallFunc::create([this] {
        //setLocalZOrder(MainDepot().localZOrderForActiveCard());
    }));
    Actions.pushBack(Action);
    Actions.pushBack(CallFunc::create([this] {
        //setLocalZOrder(MainDepot().localZOrderForPassiveCard());
    }));
    
    return Sequence::create(Actions);
}

FiniteTimeAction* Card::actionForFlipToFront() {
    Vec3 R = Vec3(0.f, 0.f, 0.f);
    float EaseRate = 2.f;
    
    return EaseOut::create(RotateTo::create(durationForCardFlip(), R), EaseRate);
}

FiniteTimeAction* Card::actionForFlipToBack() {
    Vec3 R = Vec3(0.f, -180.f, 0.f);
    float EaseRate = 2.f;
    
    return EaseOut::create(RotateTo::create(durationForCardFlip(), R), EaseRate);
}

FiniteTimeAction* Card::actionForVibration() {
    return actionForVibration(getPosition());
}

FiniteTimeAction* Card::actionForVibration(Point P) {
    float ShakeRate = 0.15f;
    float D = durationForCardShake();
    
    Size CS = getContentSize();
    
    Point Left = Point(P.x - CS.width * ShakeRate, P.y);
    Point Right = Point(P.x + CS.width * ShakeRate, P.y);
    
    size_t ActionCount = 4;
    auto ToLeft = MoveTo::create(D / (float)ActionCount, Left);
    auto ToRight = MoveTo::create(D / (float)ActionCount, Right);
    auto ToCenter = MoveTo::create(D / (float)ActionCount, P);
    
    return Sequence::create(ToLeft,
                            ToRight,
                            ToLeft,
                            ToCenter,
                            nullptr);
}

FiniteTimeAction* Card::actionForShake() {
    return actionForShake(getPosition());
}

FiniteTimeAction* Card::actionForShake(Point P) {
    float ShakeAngle = 5.f;
    float D = durationForCardShake();
    
    Vec3 R = getRotation3D();

    // NB(xenosoz, 2016): We need extra caution for picking rotation when card is shaking.
    //   That's why we throw out R.z here.
    Vec3 LeftR = Vec3(R.x, R.y, 0.f - ShakeAngle);
    Vec3 RightR = Vec3(R.x, R.y, 0.f + ShakeAngle);
    Vec3 CenterR = Vec3(R.x, R.y, 0.f);
    
    size_t ActionCount = 6;
    auto ToLeft = RotateTo::create(D / (float)ActionCount, LeftR);
    auto ToRight = RotateTo::create(D / (float)ActionCount, RightR);
    auto ToCenter = RotateTo::create(D / (float)ActionCount, CenterR);
    
    return Sequence::create(ToLeft, ToRight,
                            ToLeft, ToRight,
                            ToLeft, ToCenter, nullptr);
}

FiniteTimeAction* Card::actionForCleanUpRotation() {
    Vec3 R = getRotation3D();
    
    return RotateTo::create(0.f, Vec3(0.f, R.y, 0.f));
}

void Card::setToFront() {
    Vec3 R = Vec3(0.f, 0.f, 0.f);
    setRotation3D(R);
}

void Card::setToBack() {
    Vec3 R = Vec3(0.f, -180.f, 0.f);
    setRotation3D(R);
}

void Card::flipToFront() {
    stopAllActions();
    runAction(actionForFlipToFront());
}

void Card::flipToBack() {
    stopAllActions();
    runAction(actionForFlipToBack());
}

void Card::shake() {
    stopAllActions();
    runAction(actionForShake());
}

Size Card::defaultSize() {
    return contentSize();
}

void Card::clearInternals() {
    setContentSize(contentSize());
    TouchEventEndedPrematually = false;
    
    TouchEnabled.update(true);

    TitleText.OnValueUpdate = [this](string&) {
        if (!TitleLabel) { return; }
        TitleLabel->setString(TitleText());
    };
}

void Card::refreshChildNodes() {
    removeAllChildren();
    MainDepot Depot;
    Size CS = getContentSize();

    FrontFace = ([&] {
        auto It = Button::create(contentSkinFront());
        It->setAnchorPoint(Vec2::ANCHOR_MIDDLE);
        It->setPosition(Point(CS / 2.f));
        It->setZoomScale(0.f);

        It->addTouchEventListener([this, It](Ref*, Widget::TouchEventType E,
                                             Touch* T, Event*)
        {
            if (!TouchEnabled()) { return; }
            auto Guard = NodeScopeGuard(this);
            MainDepot Depot;

            switch (E) {
                case Widget::TouchEventType::BEGAN: {
                    setLocalZOrder(Depot.localZOrderForActiveCard());
                    if (OnFrontFaceTouchDidBegin)
                        OnFrontFaceTouchDidBegin(*this);
                    break;
                }
                case Widget::TouchEventType::MOVED: {
                    if (!TouchEventEndedPrematually)
                    {
                        auto P = getParent();
                        if (P) {
                            Vec2 InstantDelta = P->convertToNodeSpace(T->getDelta());
                            Vec2 Delta = P->convertToNodeSpace(T->getLocation() - T->getStartLocation());
                            
                            // NB(xenosoz, 2016): Move along the drag.
                            setPosition(getPosition() + InstantDelta);
                            
                            // NB(xenosoz, 2016): Fire event prematually.
                            float Threshold = Point(getContentSize()).length() * 0.10f;
                            if (Delta.length() > Threshold && OnFrontFaceClicked) {
                                OnFrontFaceClicked(*this);

                                TouchEventEndedPrematually = true;
                            }
                        }
                    }
                    break;
                }
                case Widget::TouchEventType::CANCELED: {
                    setLocalZOrder(Depot.localZOrderForPassiveCard());
                    
                    if (OnFrontFaceTouchDidCancel) {
                        OnFrontFaceTouchDidCancel(*this);
                    }
                    TouchEventEndedPrematually = false;
                    break;
                }
                case Widget::TouchEventType::ENDED: {
                    setLocalZOrder(Depot.localZOrderForPassiveCard());
                    
                    if (OnFrontFaceTouchDidEnd) {
                        OnFrontFaceTouchDidEnd(*this);
                    }
                    
                    if (!TouchEventEndedPrematually && OnFrontFaceClicked) {
                        OnFrontFaceClicked(*this);
                    }

                    TouchEventEndedPrematually = false;
                    break;
                }
            }
        });

        addChild(It);
        return It;
    }());
    
    TitleLabel = ([&] {
        auto It = Label::createWithSystemFont(TitleText(), Depot.defaultFont(), titleFontSize());
        It->setAnchorPoint(Vec2::ANCHOR_MIDDLE);
        It->setPosition(Point(FrontFace->getContentSize() / 2.f) + Vec2(0.f, -10.f));
        
        It->setTextColor(titleFontColor());

        FrontFace->addChild(It);
        return It;
    }());

    BackFace = ([&] {
        auto It = Button::create(contentSkinBack());
        It->setAnchorPoint(Vec2::ANCHOR_MIDDLE);
        It->setPosition(Point(CS / 2.f));
        It->setZoomScale(0.f);
        
        It->addClickEventListener([this](Ref*, Touch*, Event*) {
            if (!TouchEnabled()) { return; }
            auto Guard = NodeScopeGuard(this);

            if (OnBackFaceClicked)
                OnBackFaceClicked(*this);
        });

        addChild(It);
        return It;
    }());
}

END_NS_MOVINGINSECTS
